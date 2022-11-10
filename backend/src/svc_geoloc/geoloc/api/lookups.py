import datetime
import tshared.lookups.base
import tortoise.timezone
from .. import models
from base3.decorators import route, api

db_connection = 'conn_geoloc'

tbl2model = {
    'countries': {'model': models.Country, 'translations': models.TranslationCountry}
    # {{ tbl2model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
}


@route('/lookups/init')
class GeoLocInitLookupsHandler(tshared.lookups.base.BaseInitAllLookupsHandler):

    @api()
    async def post(self, lookups: dict):
        """
        Post lookup. TODO

        Parameters:
            lookups (body):

        RequestBody:
            @geoloc/POST_201_documentation_post.request_body.json

        Responses:
            @geoloc/POST_201_documentation_post.json
        """

        return await super().post(lookups, db_connection, tbl2model)


@route('/lookups')
class GeoLocAllLookupsHandler(tshared.lookups.base.BaseAllLookupsHandler):

    @api()
    async def get(self, format: str = 'default', lang: str = 'default', format_frontend_key: str = 'code',
                  frontend_format: str = 'list'):
        """
        Get lookups. TODO

        Parameters:
            lang (query): Language of response
            format (query):
            format_frontend_key (query):
            frontend_format (query):

        Responses:
            @geoloc/GET_200_documentation_get.json
        """

        return await super().get(db_connection, tbl2model, format=format, lang=lang,
                                 format_frontend_key=format_frontend_key, frontend_format=frontend_format)


@route('/lookups/:table')
class GeoLocSingleLookupHandler(tshared.lookups.base.BaseSingleLookupHandler):
    """
    Parameters:
        table (path): Table
    """

    async def get_countries(self, db_connection, last_updated, index_by):
        filters = {}
        if last_updated:
            if tortoise.timezone.is_naive(last_updated):
                last_updated = tortoise.timezone.make_aware(last_updated)

            filters['last_updated__gt'] = last_updated

        all_countries = await models.Country.filter(**filters).all()  # .prefetch_related('translations').all()

        res = {str(c.id): {'id': str(c.id), 'code': c.code, 'en_value': c.en_value, 'local_value': c.local_value} for c
               in all_countries}

        return {"last_updated": None, "items": res}

    @api()
    async def get(self, table: str, last_updated: datetime.datetime = None, index_by: str = 'id'):
        """
        Get lookups. TODO

        Parameters:
            last_updated (query):
            index_by (query):

        Responses:
            @geoloc/GET_200_documentation_get.json
        """
        if table == 'countries':
            return await self.get_countries(db_connection, last_updated=last_updated, index_by=index_by)

        return await super().get(table, db_connection, tbl2model, last_updated=last_updated, index_by=index_by)
