from spudmart.upload.models import UploadedFile


def reset_cover_image(entity):
    entity.cover_image = None
    entity.save()


def save_cover_image_from_request(entity, request):
    image_id = request.POST['id'].split('/')[3][:-12]

    uploaded_file = UploadedFile.objects.get(id=image_id)

    entity.cover_image = uploaded_file
    entity.save()