from google.appengine.api import images, files
from google.appengine.api import blobstore
from google.appengine.api.images import get_serving_url
from google.appengine.ext.blobstore import BlobReader
from spudmart.upload.forms import UploadForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from spudmart.upload.models import UploadedFile
from spudmart.upload.utils import resize_image, serve_file
from django.utils.datastructures import MultiValueDict
import simplejson


def get_upload_url(request):
    return HttpResponse(blobstore.create_upload_url('/upload/upload_image_endpoint'))


def upload_image_endpoint(request):
    json_dict = { 'uploaded_files' : [] }
    width = request.POST.get('width', False)
    height = request.POST.get('height', False)
    for i, _ in enumerate(request.FILES):
        files_dict = {}
        files_dict['file'] = [request.FILES['file-%s' % i]]
        FILES = MultiValueDict(files_dict)
        form = UploadForm(request.POST, FILES)
        model = form.save(False)
        if width and height:
            model.file = resize_image(model.file.file, int(width), int(height))
        model.user = request.user
        model.content_type = FILES['file'].content_type
        model.save()
        json_dict['uploaded_files'].append('/file/serve/%s' % model.pk)
    return HttpResponse(simplejson.dumps(json_dict))


def serve_uploaded_file(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, pk=file_id)

    response = HttpResponse()
    response['Content-Type'] = uploaded_file.content_type
    response['Cache-Control'] = "public, max-age=" + str(3600*24*30)
    response['ETag'] = str(uploaded_file.id)

    if uploaded_file.file.file.blobstore_info is None:
        return HttpResponseNotFound()
    elif request.GET.get('max_dim', False):
        blob_key = str(uploaded_file.file.file.blobstore_info.key())
        return HttpResponseRedirect('%s=s%s' %
                                    (get_serving_url(blob_key),
                                    request.GET.get('max_dim'))
                                    )

    return serve_file(uploaded_file, response)


def get_croppic_upload(request):
    return HttpResponse(blobstore.create_upload_url('/upload/croppic_upload_endpoint'))


def croppic_upload_endpoint(request):
    json_dict = {'status': 'success'}
    files_dict = {'file': [request.FILES['img']]}
    FILES = MultiValueDict(files_dict)
    form = UploadForm(request.POST, FILES)
    model = form.save(False)
    model.user = request.user
    model.content_type = FILES['file'].content_type
    model.save()
    blob_key = str(model.file.file.blobstore_info.key())
    i = images.Image(blob_key=blob_key)
    i.rotate(0)
    i.execute_transforms()
    json_dict['width'] = i.width / 2
    json_dict['height'] = i.height / 2
    json_dict['url'] = ('/file/serve/%s' % model.pk)
    return HttpResponse(simplejson.dumps(json_dict))


def translate_dimension_int(dimension):
    """
    Translates a POST attribute from str to rounded int

    Also doubles to get the proper pixel dimension

    :param dimension: string from POST request which is a number
    :type dimension: str
    :return: rounded, doubled int version of number
    :rtype: int
    """
    dim_float = float(dimension)
    return int(round(dim_float * 2, 0))


def translate_dimension_float(dimension):
    """
    Translates a POST attribute from str to float

    Also doubles to get the proper pixel dimension

    :param dimension: string from POST request which is a number
    :type dimension: str
    :return: doubled float version of number
    :rtype: float
    """
    return float(dimension) * 2


def croppic_crop(request):
    """
    Crops the cover image to specs supplied by croppic

    :param request: a POST request with imgUrl, imgW, imgH, imgX1,
        imgY1, cropW, and cropH parameters, supplied by croppic
    :return: a json-formatted dict of {status:success,
        url:<URL to cropped image>}
    """

    imgid = request.POST['imgUrl'].split('/')[-1]
    imgW = translate_dimension_float(request.POST['imgW'])
    imgH = translate_dimension_float(request.POST['imgH'])
    X1 = translate_dimension_float(request.POST['imgX1'])
    Y1 = translate_dimension_float(request.POST['imgY1'])
    cropW = translate_dimension_int(request.POST['cropW'])
    cropH = translate_dimension_int(request.POST['cropH'])

    new_file = UploadedFile()
    old = UploadedFile.objects.get(id=imgid)
    blob_key = str(old.file.file.blobstore_info.key())

    if imgW >= cropW and imgH >= cropH:
        i = images.Image(blob_key=blob_key)
        i.crop(X1 / imgW, Y1 / imgH, (cropW + X1) / imgW, (cropH + Y1) / imgH)
        resized = i.execute_transforms()
        file_name = files.blobstore.create(mime_type='image/png')
        with files.open(file_name, 'a') as f:
            f.write(resized)
        files.finalize(file_name)

        blob_key = str(files.blobstore.get_blob_key(file_name))
        new_file.file = blob_key
        new_file.save()
    else:
        new_file = old

    return HttpResponse(
        simplejson.dumps({
                         "status": "success",
                         "url": "/file/serve/%s?max_dim=600" % new_file.id
                         })
        )