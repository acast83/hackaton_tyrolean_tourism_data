import datetime
from base3.decorators import route, api

import tshared.lookups.base
from .. import models


db_connection = 'conn_telegram'

tbl2model = {
    'message_sending_status': {'model': models.LookupMessageSendingStatus, 'translations': models.TranslationLookupMessageSendingStatus},
    # {{ tbl2model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
}


@route('/lookups/init')
class TelegramInitLookupsHandler(tshared.lookups.base.BaseInitAllLookupsHandler):

    @api()
    async def post(self, lookups: dict):
        return await super().post(lookups, db_connection, tbl2model)


@route('/lookups')
class TelegramAllLookupsHandler(tshared.lookups.base.BaseAllLookupsHandler):

    @api()
    async def get(self):
        return await super().get(db_connection, tbl2model)


@route('/lookups/:table')
class TelegramLookupHandler(tshared.lookups.base.BaseSingleLookupHandler):

    @api()
    async def get(self, table: str, last_updated: datetime.datetime = None, index_by: str = 'id'):
        return await super().get(table, db_connection, tbl2model, last_updated=last_updated, index_by=index_by)
