import logging
import settings
from webengine import route
from webapp2_extras import routes
from google.appengine.ext import ndb
from webengine.models import User


@route('/')
def index(handler):
    handler.render('index.html')

@route('/<some_id>')
def index(handler, some_id):
    logging.info(some_id)
    handler.render('index.html')


#Setup a custom handler
@route('/upload', handler=blobstore_handlers.BlobstoreUploadHandler, route_type=Route)
def upload_image(handler):
    logging.info(handler.request.params)
    upload_files = handler.get_uploads()  # 'file' is file upload field in the form
    logging.info(upload_files)
    blob_info = upload_files[0]
    handler.response.headers['Content-Type'] = 'application/json'
    resp = {
        'content_type': blob_info.content_type,
        'filename': blob_info.filename,
        'size': blob_info.size,
        'key': str(blob_info.key())
    }
    handler.response.out.write(json.dumps(resp))

