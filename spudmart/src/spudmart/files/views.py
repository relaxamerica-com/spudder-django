from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from spudmart.files.models import UploadedFile
from spudmart.files.utils import get_blobstore_reader, serve_file


def serve_uploaded_file(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, pk=file_id)

    response = HttpResponse()
    response['Content-Type'] = uploaded_file.content_type
    response['Cache-Control'] = "public, max-age=" + str(3600*24*30)
    response['ETag'] = str(uploaded_file.id)

    if uploaded_file.file.file.blobstore_info is None:
        return HttpResponseNotFound()

    return serve_file(uploaded_file, request, response)

