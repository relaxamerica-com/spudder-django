from google.appengine.api import blobstore
from google.appengine.ext.blobstore import BlobReader
from spudmart.upload.forms import UploadForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from spudmart.upload.models import UploadedFile
from spudmart.upload.utils import resize_image
import logging
from django.utils.datastructures import MultiValueDict
import simplejson

def get_upload_url(request):
    return HttpResponse(blobstore.create_upload_url('/upload/upload_image_endpoint'))

def upload_image_endpoint(request):
    json_dict = { 'uploaded_files' : [] }
    width = request.POST.get('width', 200)
    height = request.POST.get('height', 300)
    for i, _ in enumerate(request.FILES):
        files_dict = {}
        files_dict['file'] = [request.FILES['file-%s' % i]]
        FILES = MultiValueDict(files_dict)
        form = UploadForm(request.POST, FILES)
        model = form.save(False)
        model.file = resize_image(model.file.file, int(width), int(height))
        model.user = request.user
        model.content_type = FILES['file'].content_type
        model.save()
        json_dict['uploaded_files'].append('/file/serve/%s' % model.pk)
    return HttpResponse(simplejson.dumps(json_dict))

def upload_image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if len(request.FILES) > 0: 
            model = form.save(False)
            
            model.file = resize_image(model.file.file, 300, 200)
            model.user = request.user
            model.content_type = request.FILES['file'].content_type
            model.save()
            return HttpResponseRedirect('/profile/edit_profile')
    
    upload_url = blobstore.create_upload_url('/upload/upload_image')
    form = UploadForm()
    
    return render(request, 'upload/upload_image.html', { 'form' : form, 'upload_url' : upload_url })

def serve_blob(request, file_id):
    upload = get_object_or_404(UploadedFile, pk=file_id)
    response = HttpResponse()
    response['Accept-Ranges'] = 'bytes'
    response['Content-Type'] = upload.content_type
    if upload.content_type != 'video/mp4':
        response['Cache-Control'] = "public, max-age=" + str(3600*24*30)
    response['ETag'] = str(upload.id)
    if 'HTTP_RANGE' not in request.META:
        if upload.file.file.blobstore_info.size < 32 * 1024 * 1024:
            reader = BlobReader(upload.file.file.blobstore_info)
            response.content = reader.read()
        else:
            response['X-AppEngine-BlobKey'] = str(upload.file.file.blobstore_info.key())
            return response
    else:
        reader = BlobReader(upload.file.file.blobstore_info)
        response.status_code = 206
        range_string = request.META['HTTP_RANGE']
        bytes_string = range_string.split('=')[1]
        limits = bytes_string.split('-')
        reader.seek(int(limits[0]))
        if limits[1]:
            response.content = reader.read(int(limits[1])-int(limits[0])+1)
            response['Content-Range'] = 'bytes %s-%s/%s' % (limits[0], int(limits[1]), upload.file.file.blobstore_info.size)
        else:
            response.content = reader.read(int(upload.file.file.blobstore_info.size) - int(limits[0]))
            response['Content-Range'] = 'bytes %s-%s/%s' % (limits[0], int(upload.file.file.blobstore_info.size)-1, upload.file.file.blobstore_info.size)
    return response