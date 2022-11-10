from base3.core import Base, Base_
from tortoise.transactions import in_transaction
import base3.decorators
from base3 import http
import tornado
import uuid


class BaseStatic(Base_, tornado.web.StaticFileHandler):

    pass

    # def __int__(self):
    #     super().__init__()
    #

class BaseOptionsHandler(Base):
    model_Option = None

    # db_connection = None

    @base3.decorators.api(weak=True)
    async def get(self, key=None):

        id_tenant = getattr(self,'id_tenant', uuid.UUID('00000000-0000-0000-0000-000000000000'))
        id_user = getattr(self,'id_user',  uuid.UUID('00000000-0000-0000-0000-000000000000'))

        if not key:
            return {o.key: o.value for o in await self.model_Option.filter(id_tenant=self.id_tenant).all()}
        else:
            option = await self.model_Option.filter(key=key, id_tenant=self.id_tenant).get_or_none()
            if not option:
                raise http.HttpErrorNotFound
            return option.value


    @base3.decorators.api(weak=True)
    async def post(self, key: str, value: str):
        # async with in_transaction(connection_name=self.db_connection):

        id_tenant = getattr(self,'id_tenant', uuid.UUID('00000000-0000-0000-0000-000000000000'))
        id_user = getattr(self,'id_user',  uuid.UUID('00000000-0000-0000-0000-000000000000'))

        o = await self.model_Option.filter(id_tenant=id_tenant, key=key).get_or_none()

        if not o:
            o = self.model_Option(
                id_tenant=id_tenant,
                created_by=id_user,
                last_updated_by=id_user,
                key=key,
                value=value,
            )
            await o.save()

        elif o.value != value:
                o.last_updated_by = id_user
                o.value = value
                await o.save()

        return {'id': o.id}, http.status.CREATED
