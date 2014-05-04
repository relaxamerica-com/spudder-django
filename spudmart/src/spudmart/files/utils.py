from google.appengine.ext.blobstore import BlobReader, InternalError

SIZE_32_MB = 32 * 1024 * 1024
GAE_LIMIT = 1024 * 1024 * 5
RETRY_COUNT = 10


def get_blobstore_reader(uploaded_file):
    return BlobReader(str(uploaded_file.file.file.blobstore_info.key()))


def serve_file(uploaded_file, request, response):
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