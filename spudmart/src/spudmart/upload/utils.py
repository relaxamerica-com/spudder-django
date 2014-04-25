from google.appengine.api import images, files

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
