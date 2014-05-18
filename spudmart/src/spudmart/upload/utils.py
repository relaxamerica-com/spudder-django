from google.appengine.api import images, files
from google.appengine.ext.blobstore import BlobReader, InternalError
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from spudmart.upload.models import UploadedFile

RETRY_COUNT = 10


def resize_image(image_file, width, height):
    image = images.Image(blob_key=image_file.blobstore_info)
    image.resize(width, height)
    resized = image.execute_transforms(output_encoding=images.PNG)
    file_name = files.blobstore.create(mime_type='image/png')
    with files.open(file_name, 'a') as f:
        f.write(resized)
    files.finalize(file_name)

    blob_key = files.blobstore.get_blob_key(file_name)
    return str(blob_key)


def get_blobstore_reader(uploaded_file):
    return BlobReader(str(uploaded_file.file.file.blobstore_info.key()))


def serve_file(uploaded_file, response):
    reader = get_blobstore_reader(uploaded_file)

    retry = 0
    while retry < RETRY_COUNT:
        try:
            response.content = reader.read()

            retry = RETRY_COUNT
        except InternalError, e:
            retry += 1
            if retry == RETRY_COUNT:
                reader.close()
                raise e

    reader.close()
    return response