import os
import uuid
import json
import base64
import hashlib
import base3.handlers
import pdf2image
from . import get_db_connection, config
from .. import models
from base3 import http
from base3.core import Base
from base3.decorators import route, api
from tortoise.transactions import in_transaction
from PIL import Image
import tshared.ipc.flows as ipc_flow

db_connection = 'conn_documents'
STATIC_LOCATION_PATH = '/api/v3/files/static/'


@route('/about')
class DocumentsAboutHandler(Base):

    @api(auth=False)
    async def get(self):
        """
        Get about information

        Responses:
           @documents/GET_200_documentation_about.json
        """

        return {'service': 'documents'}


@route('/options')
class DocumentsOptionsHandler(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


def generate_png_from_pdf(source_pdf, dpi=96, output_folder='/tmp/', output_file=None,
                          from_page=0, to_page=1, fmt='png'):
    res = []
    try:
        images = pdf2image.convert_from_path(source_pdf, dpi=dpi, output_folder='/tmp/',
                                             first_page=from_page, last_page=to_page, fmt=fmt)

        for page in range(from_page, to_page):

            if not output_file:
                fname = f'{output_folder}/{uuid.uuid4()}-{page}.{fmt}'
            else:
                if to_page - from_page == 1:
                    fname = f'{output_folder}/{output_file}.{fmt}'
                else:
                    fname = f'{output_folder}/{output_file}-{page}.{fmt}'

            res.append(fname)
            images[page].save(fname)

            os.unlink(images[page].filename)

            return res

    except Exception as e:
        raise http.HttpInternalServerError(id_message='ERROR_MAKING_THUMBNAIL', message=str(e))


def mk_thumb(src, size=(256, 256), orientation=0):
    t = src.split('.')[-1]
    fn = '.'.join(src.split('.')[:-1])

    img = Image.open(f'{fn}.{t}')

    w, h = img.size

    if w > h:
        top = 0
        down = h
        left = int(round(w / 2 - h / 2, 0))
        right = int(round(w / 2 + h / 2, 0))
    else:
        left = 0
        right = w
        top = int(round(h / 2 - w / 2, 0))
        down = int(round(h / 2 + w / 2, 0))

    img = img.crop((left, top, right, down))

    if type(size) in (tuple, list) and len(size) == 2:
        sizew = size[0]
        sizeh = size[1]

    else:
        sizew = size
        sizeh = size

    img = img.resize((sizew, sizeh), resample=Image.LANCZOS)
    img = img.rotate(int(orientation))

    target = f'{fn}.thumbnail.{t}'
    img.save(target)
    return target


def do_make_thumbnail(document_type, source_file):
    try:
        if document_type == 'pdf':
            sfs = [x for x in source_file.split('/')]  # source file split
            output_folder = '/'.join(sfs[:-1])
            output_file = sfs[-1].split('.')[0] + '.thumbnail'

            res = generate_png_from_pdf(source_file, output_folder=output_folder, output_file=output_file)
            return res[0]
        elif document_type == "png" or document_type == "jpeg" or document_type == "jpeg" or document_type == "bmp":
            return mk_thumb(source_file)
        else:
            return None


    except Exception as e:
        return None


def named_size(size):
    if size <= 1024:
        return f'{size} b'
    if size <= 1024 * 1024:
        return f'{round(size / 1024, 2)} kb'
    if size <= 1024 * 1024 * 1000:
        return f'{round(size / 1024 / 1000, 2)} mb'

    return f'{round(size / 1024 / 1000 / 1000, 2)} gb'


@route('/-/:id_document')
class SingleDocumentHandler(base3.handlers.Base):
    """
    Parameters:
        id_document (path): Document ID
    """

    @api()
    async def get(self, id_document: uuid.UUID, fields: str = None):
        """
        Get document TODO

        Parameters:
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Document.default_fields

        Responses:
            TODO
        """

        if fields and ('absolute_location' in fields or 'absolute_thumbnail_location' in fields):
            fields += ',location'

        res = await models.Document.base_get(
            json_filters={'id_tenant': self.id_tenant, 'id': id_document},
            expected_one_item=True,
            fields=fields, prefetched=['cache11'])

        if not fields or 'absolute_location' in fields:
            res['absolute_location'] = config['storage'] + res['location']
        if not fields or 'absolute_thumbnail_location' in fields:
            res['absolute_thumbnail_location'] = (config['storage'] + res['thumbnail']) if res[
                'thumbnail'] else None

        return res

    @api()
    async def patch(self, id_document: uuid.UUID,
                    filename: str = None,
                    thumbnail_data_b64: str = None,
                    thumbnail_format: str = 'png'):
        """
        Patch TODO

        Parameters:
            filename (body): TODO
            thumbnail_data_b64 (body): TODO
            thumbnail_format (body): TODO

        RequestBody:

        Responses:

        """
        try:
            doc = await models.Document.base_get(
                json_filters={'id_tenant': self.id_tenant, 'id': id_document},
                return_awaitable_orm_objects=True,
                expected_one_item=True,
                no_paginate=True,
                prefetched=['cache11'])

        except Exception as e:
            raise http.HttpErrorNotFound(id_message='DOCUMENT_NOT_FOUND')

        #
        # TODO: use this to allow update by user !!!!
        #
        #
        # owner_rwd_policy = fields.JSONField(null=False, default={'read': True, 'write': True, 'delete': True})
        # default_user_groups_rwd_policy = fields.JSONField(null=False,
        #                                                   default={'read': True, 'write': False, 'delete': False})
        # default_users_rwd_policy = fields.JSONField(null=False, default={'read': True, 'write': False, 'delete': False})
        # default_all_unauthorized_rwd_policy = fields.JSONField(null=False,
        #                                                        default={'read': False, 'write': False, 'delete': False})

        updated = []

        async with in_transaction(connection_name=get_db_connection()):

            if filename:
                if doc.filename != filename:
                    doc.filename = filename
                    await doc.save()

                    updated.append('filename')

            if thumbnail_data_b64:

                digest = doc.hash256

                if not os.path.isdir(config['storage']):
                    try:
                        os.mkdir(config['storage'])
                    except Exception as e:
                        raise http.HttpInternalServerError(id_message='ERROR_CREATING_STORAGE_FOLDER')

                f1 = config['storage'] + '/' + digest[:2]
                if not os.path.isdir(f1):
                    os.mkdir(f1)

                f2 = f1 + '/' + digest[2:4]
                if not os.path.isdir(f2):
                    os.mkdir(f2)

                file = f2 + '/' + digest + '.thumbnail.' + thumbnail_format
                if not os.path.isfile(file):
                    with open(file, 'wb') as f:
                        content = base64.b64decode(thumbnail_data_b64.encode('ascii'))
                        f.write(content)

                doc.thumbnail = file[len(config['storage']):]

                await doc.save()

                updated.append('thumbnail')

    @api()
    async def delete(self, id_document: uuid.UUID, ):
        document = await models.Document.filter(id_tenant=self.id_tenant, id=id_document, active=True).get_or_none()
        if not document:
            raise http.HttpErrorNotFound(id_message="DOCUMENT_NOT_FOUND")
        document.active = None
        await document.save()
        return


@route('/:instance/:id_instance')
class DocumentsHandler(base3.handlers.Base):
    """
    Parameters:
        instance (path):     TODO
        id_instance (path):  TODO
    """

    @api()
    async def get(self, instance: str, id_instance: uuid, no_paginate=False, page=1, per_page=100, fields=None,
                  order_by='created', search=None, language: str = 'default', filters: dict = None, limit: int = None):
        """
        Get document instance   TODO

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Document.default_fields
            order_by (query): Result order
                enum: @Document.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @documents/test_documentation_get_documents_instance.json
        """
        try:

            if not filters:
                filters = {}

            if type(filters) == str:
                filters = json.loads(filters)

            no_paginate = no_paginate and no_paginate in ('True', 'true', 'yes', '1', 1, True)

            filters['id_tenant'] = self.id_tenant
            filters['instance'] = instance
            filters['id_instance'] = id_instance
            #
            # q = await models.Document.base_get(request=self.request,
            #
            #                                         debug_return_query=True,
            #
            #                                         json_filters=filters,
            #                                         force_limit=limit,
            #                                         expected_one_item=False,
            #                                         no_paginate=no_paginate, page=page, per_page=per_page, fields=fields, order_by=order_by, search=search,
            #                                         language=language, lowercased_search_field='en_value', prefetched=['cache11'])

            result = await models.Document.base_get(request=self.request,
                                                    json_filters=filters,
                                                    force_limit=limit,
                                                    expected_one_item=False,
                                                    no_paginate=no_paginate, page=page, per_page=per_page, fields=fields, order_by=order_by, search=search,
                                                    language=language, lowercased_search_field='en_value', prefetched=['cache11'])

            if not no_paginate and not result["items"]:
                return {
                    'items': [],
                    'summary': {}
                }
        except Exception as e:
            raise
        if not no_paginate:
            data = result["items"]
        else:
            data = result

        for doc in data:

            doc['url'] = f'{STATIC_LOCATION_PATH}{doc["id"]}.{doc["filetype"]}?download=true&r={uuid.uuid4()}'
            if 'thumbnail' in doc and doc['thumbnail']:
                doc['thumbnail_url'] = f'{STATIC_LOCATION_PATH}{doc["id"]}.thumbnail.{doc["filetype"]}?r={uuid.uuid4()}'
            else:
                doc['thumbnail_url'] = None

            if 'filesize' in doc:
                doc["named_size"] = named_size(doc['filesize'])

            if 'location' in doc:
                del doc['location']
            if 'thumbnail' in doc:
                del doc['thumbnail']

            # res = {
            #     'id': document.id,
            #     "created": document.created,
            #     "url": f'/api/v3/files/{document.id}.{document.filetype}',
            #     "filename": document.filename,
            #     "size": document.filesize,
            #     "named_size": named_size(document.filesize),
            #     "icon": "/file.png",  # Mokapovao
            # }

            # doc["location"] = f'{config["storage"]}{doc["location"]}' if "location" in doc and doc["location"] else None
            # doc["thumbnail"] = f'{config["storage"]}{doc["thumbnail"]}' if "thumbnail" in doc and doc["thumbnail"] else None
            # doc["named_size"] = named_size(int(doc["filesize"])) if doc["filesize"] else None
            # doc["icon"] = "/file.png"
            # doc["path"] = f"/{doc['location'].split('/')[-1]}" if doc['location'] else None

        return result

        # res = {
        #
        #     "created": document.created,
        #     'location': file,
        #     "icon": "/file.png",  # Mokapovao
        #     'id': document.id,
        #     "filename": document.filename,
        #     "named_size": named_size(document.filesize),
        #     "path": f"/{document.location.split('/')[-1]}",
        #     "filesize": document.filesize,
        #     'thumbnail': thmb_loc,
        #     "filetype": document.filetype
        #
        # }

    @api()
    async def post(self, instance: str, id_instance: str, filename: str, bse64encoded: str,
                   make_thumbnail: bool = True):
        """
        Post document   TODO

        Parameters:
            filename (body): File name
            bse64encoded (body): TODO
            make_thumbnail (body): TODO

        RequestBody:
            @documents/POST_200_documentation_post_documents_instance.request_body.json

        Responses:
            @documents/POST_200_documentation_post_documents_instance.json
        """

        # self.log.critical(f'trying to fetch document {instance}/{id_instance}')

        if instance == '-':
            raise http.HttpNotAcceptable(id_message='NOT_ACCEPTABLE_INSTANCE')

        if True:
            # async with in_transaction(connection_name=get_db_connection()):
            body = json.loads(self.request.body) if self.request.body else {}
            body['instance'] = instance
            body['id_instance'] = id_instance

            if 'filetype' in body:
                body['filetype'] = body['filetype'].lower()

            document = await models.Document.base_create(handler=self, body=body, skip_uid=True)

            # self.log.critical(f'trying to fetch document = {document} id{document.id if document else None}')

            if document:

                # self.log.critical('d1')

                if not os.path.isdir(config['storage']):
                    try:
                        os.mkdir(config['storage'])
                    except Exception as e:
                        raise http.HttpInternalServerError(id_message='ERROR_CREATING_STORAGE_FOLDER')

                # self.log.critical('d2')

                extension = filename.split('.')[-1].lower()
                content = base64.b64decode(bse64encoded.encode('ascii'))

                m = hashlib.sha256()
                m.update(content)
                digest = m.hexdigest()

                f1 = config['storage'] + '/' + digest[:2]
                if not os.path.isdir(f1):
                    os.mkdir(f1)

                f2 = f1 + '/' + digest[2:4]
                if not os.path.isdir(f2):
                    os.mkdir(f2)

                file = f2 + '/' + digest + '.' + extension
                if not os.path.isfile(file):
                    with open(file, 'wb') as f:
                        f.write(content)

                # self.log.critical('d3')

                document.filesize = os.path.getsize(file)

                document.hash256 = digest
                document.filesize = os.path.getsize(file)

                document.location = file[len(config['storage']):]

                if not document.filetype:
                    document.filetype = file.split('.')[-1].lower()

                if make_thumbnail:
                    thmb = do_make_thumbnail(document.filetype, file)
                    thmb_loc = thmb
                    document.thumbnail = thmb[len(config['storage']):] if thmb else None

                # self.log.critical('d4')

                await document.save()
                await document.mk_cache(handler=self)
                if instance == "sales":
                    await ipc_flow.flow(handler=self, instance=instance, id_instance=uuid.UUID(id_instance),
                                        type_code='FLOW_TYPE_USER_ACTION',
                                        message="attachments added",
                                        data={'action': 'ADD_ATTACHMENT',
                                              'filename': document.filename,
                                              })

                # self.log.critical('d5')

            global STATIC_LOCATION_PATH

            res = {
                'id': document.id,
                "created": document.created,
                "url": f'{STATIC_LOCATION_PATH}{document.id}.{document.filetype}?download=true',
                "thumbnail_url": f'{STATIC_LOCATION_PATH}{document.id}.thumbnail.{document.filetype}' if document.thumbnail else None,
                "filename": document.filename,
                "size": document.filesize,
                "named_size": named_size(document.filesize),
                "icon": "/file.png",  # Mokapovao
            }

            from base3.test import test_mode
            if test_mode:
                res['file'] = file

            return res

    @api()
    async def delete(self, instance: str, id_instance: str):
        try:

            await models.Document.filter(instance=instance, id_instance=id_instance, active=True).update(active=None)
        except:
            return

    # @api()
    # async def patch(self, instance: str, id_instance: str, filename: str = None, thumbnail_data_b64: str = None,
    #                 thumbnail_format: str = 'png'):
    #     try:
    #         doc = await models.Document.base_get(
    #             json_filters={'id_tenant': self.id_tenant, 'instance': instance, 'id_instance': id_instance},
    #             return_awaitable_orm_objects=True, expected_one_item=True,
    #             no_paginate=True,
    #             prefetched=['cache11'])
    #
    #     except Exception as e:
    #         raise http.HttpErrorNotFound(id_message='DOCUMENT_NOT_FOUND')
    #
    #     #
    #     # use this to allow update by user !!!!
    #     #
    #     #
    #     # owner_rwd_policy = fields.JSONField(null=False, default={'read': True, 'write': True, 'delete': True})
    #     # default_user_groups_rwd_policy = fields.JSONField(null=False,
    #     #                                                   default={'read': True, 'write': False, 'delete': False})
    #     # default_users_rwd_policy = fields.JSONField(null=False, default={'read': True, 'write': False, 'delete': False})
    #     # default_all_unauthorized_rwd_policy = fields.JSONField(null=False,
    #     #                                                        default={'read': False, 'write': False, 'delete': False})
    #
    #     updated = []
    #
    #     async with in_transaction(connection_name=get_db_connection()):
    #
    #         if filename:
    #             if doc.filename != filename:
    #                 doc.filename = filename
    #                 await doc.save()
    #
    #                 updated.append('filename')
    #
    #         if thumbnail_data_b64:
    #
    #             digest = doc.hash256
    #
    #             if not os.path.isdir(config['storage']):
    #                 try:
    #                     os.mkdir(config['storage'])
    #                 except Exception as e:
    #                     raise http.HttpInternalServerError(id_message='ERROR_CREATING_STORAGE_FOLDER')
    #
    #             f1 = config['storage'] + '/' + digest[:2]
    #             if not os.path.isdir(f1):
    #                 os.mkdir(f1)
    #
    #             f2 = f1 + '/' + digest[2:4]
    #             if not os.path.isdir(f2):
    #                 os.mkdir(f2)
    #
    #             file = f2 + '/' + digest + '.thumbnail.' + thumbnail_format
    #             if not os.path.isfile(file):
    #                 with open(file, 'wb') as f:
    #                     content = base64.b64decode(thumbnail_data_b64.encode('ascii'))
    #                     f.write(content)
    #
    #             doc.thumbnail = file[len(config['storage']):]
    #             await doc.save()
    #
    #             updated.append('thumbnail')

    # @api()
    # async def post(self, instance: str, id_instance: uuid, filename: str, bse64encoded: str):
    #
    #     async with in_transaction(connection_name=get_db_connection()):
    #         body = json.loads(self.request.body) if self.request.body else {}
    #         body['instance'] = instance
    #         body['id_instance'] = id_instance
    #
    #         document = await models.Document.base_create(handler=self, body=body, skip_uid=True)
    #         if document:
    #             await document.save()
    #             await document.mk_cache(handler=self)
    #
    #         from . import config
    #         return config
    #
    #         return await document.serialize(fields=('id',)), http.status.CREATED