from google.appengine.api import blobstore
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

    return serve_file(uploaded_file, response)