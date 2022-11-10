import datetime
import tshared.lookups.base
from .. import models
from base3.decorators import route, api
from ..api import get_db_connection



tbl2model = {
    'flow_types': {'model': models.LookupFlowType, 'translations': models.TranslationFlowType},
    'flow_visibility': {'model': models.LookupFlowVisibility, 'translations': models.TranslationLookupFlowVisibility},
    'flow_priorities': {'model': models.LookupFlowPriorities, 'translations': models.TranslationLookupFlowPriorities},
    # {{ tbl2model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
}


@route('/lookups/init')
class FlowsInitLookupsHandler(tshared.lookups.base.BaseInitAllLookupsHandler):

    @api()
    async def post(self, lookups: dict):
        """
        Post lookup TODO

        Parameters:
            lookups (body): Lookup name

        RequestBody:
            @flows/POST_201_documentation_post.request_body.json

        Responses:
            @flows/POST_201_documentation_post.json
        """

        return await super().post(lookups, get_db_connection(), tbl2model)


@route('/lookups')
class FlowsAllLookupsHandler(tshared.lookups.base.BaseAllLookupsHandler):

    @api()
    async def get(self, format: str = 'default', lang: str = 'default', format_frontend_key: str = 'code',
                  frontend_format: str = 'list'):
        """
        Get lookups TODO

        Parameters:
            format (query):
            lang (query): Language of response
            format_frontend_key (query):
            frontend_format (query):

        Responses:
            @flows/GET_200_documentation_get_lookups.json
        """

        return await super().get(get_db_connection(), tbl2model, format=format, lang=lang,
                                 format_frontend_key=format_frontend_key, frontend_format=frontend_format)


@route('/lookups/:table')
class FlowsLookupHandler(tshared.lookups.base.BaseSingleLookupHandler):

    @api()
    async def get(self, table: str, last_updated: datetime.datetime = None, index_by: str = 'id'):
        """
        Get lookup from table. TODO

        Parameters:
            table (path):
            last_updated (query):
            index_by (query):

        Responses:
            @flows/GET_200_documentation_get_lookup_from_table.json
        """
        return await super().get(table, get_db_connection(), tbl2model, last_updated=last_updated, index_by=index_by)