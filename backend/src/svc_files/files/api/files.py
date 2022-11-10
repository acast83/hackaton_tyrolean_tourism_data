import base3.handlers
from base3 import http
from base3.core import Base
from base3.decorators import route, api
import tshared.ipc.documents as ipc_documents
from collections import namedtuple
from .. import models

db_connection = 'conn_files'


@route('/about')
class FilesAboutHandler(Base):

    @api(auth=False)
    async def get(self):
        """
        Get about information

        Responses:
            @files/GET_200_documentation_get_about.json
        """
        return {'service': 'files'}


@route('/options')
class FilesOptionsHandler(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


@route('/static/:id_document_with_type', static={"path": '/tmp/storage'})
class StaticHandler(base3.handlers.BaseStatic):
    """
    Parameters:
        id_document_with_type (path): TODO
    """
    @api(weak=True, raw=True)
    async def get(self, id_document_with_type, include_body: bool = True, token: str = None, download: bool = False):
        """
        Get TODO parameters

        Parameters:
            include_body (query): TODO
            token (query):
            download (query):

        Responses:
            @files/GET_200_documentation_get_.json
        """
        print('GET = id_document_with_type',id_document_with_type)

        request = self.request

        if str(self.id_user) == "00000000-0000-0000-0000-000000000000":

            if not token:
                token = self.get_secure_cookie('token', None).decode()

            if not token:
                raise http.HttpNotAcceptable(id_message='MISSING_TOKEN')

            REQUEST = namedtuple("request", "body headers")
            request = REQUEST({}, {'Authorization': f'Bearer {token}'})

        adwt = id_document_with_type.split('.')
        id_document = adwt[0]
        type = '.'.join(adwt[1:])

        doc, code = await ipc_documents.get(request, id_document,'id,thumbnail,absolute_thumbnail_location,absolute_location,filename')

        if download:
            self.set_header('Content-Disposition', 'attachment; filename=' + doc['filename'])
        else:
            self.set_header('Content-Disposition', 'inline')

        if 'thumbnail' in type:
            path = doc['absolute_thumbnail_location']
        else:
            path = doc['absolute_location']

        if code in (200, 201, 204):
            # path = path[len('/tmp/storage'):]
            try:
                res = await super().get(path, include_body)
            except Exception as e:
                raise

            return

        raise http.HttpErrorNotFound(id_messag='DOCUMENT_NOT_FOUND')
