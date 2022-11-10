import copy
import uuid
from base3 import http
import tshared.ipc.tenants as ipc_tenants
import tshared.ipc.tickets as ipc_tickets
import tshared.ipc.bp as ipc_bp
import tshared.ipc.flows as ipc_flows
import tshared.ipc.wiki as ipc_wiki
import tshared.ipc.contacts as ipc_contacts
import tshared.ipc.sla as ipc_sla
import tshared.ipc.geoloc as ipc_geoloc
import tshared.ipc.open_messenger as ipc_open_messenger
import tshared.ipc.services as ipc_services
import tshared.ipc.pdf_generator as ipc_pdf_generator
import tshared.ipc.wallet as ipc_wallet
import asyncpg.pgproto.pgproto
import dateutil.parser
import tortoise.timezone

import tshared.ipc.kanban as ipc_kanban
import tshared.ipc.deals as ipc_deals

import tshared.ipc.messenger as ipc_messenger
import tshared.ipc.olo as ipc_olo

import tshared.ipc.conferences as ipc_conferences


# {{ import_ipc }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}


class Lookup():
    mutable = True
    name = None
    fetch_method = None
    last_updated = None
    indexes = []
    cache_by_id = {}
    cache_by_index = {}

    use_tenant = True

    objects_cache = {}

    # TODO: put this force_key_into instanced object !!!! #igor

    force_key_value = ['id', object]

    @classmethod
    async def without_tenant_create(cls, handler, script=False):
        if cls.__name__ not in cls.objects_cache:
            cls.objects_cache[cls.__name__] = await cls._create(handler)

        return cls.objects_cache

    def __getitem__(self, key):
        if self.force_key_value[0] == 'id':
            if type(key) == uuid.UUID:
                key = str(key)

        res = self.get(key, index=self.force_key_value[0])
        if self.force_key_value[1] != object:
            return res[self.force_key_value[1]]

        return res

    @classmethod
    async def create(cls, handler, script=False, force_key_value=['id', 'code']):  # use ['id',object] for whole object

        if cls.name in ('company_sites', 'companies', 'users'):
            if force_key_value == ['id', 'code']:
                force_key_value == ['id', object]

        cls.force_key_value = force_key_value

        if not cls.use_tenant:
            try:
                return await cls.without_tenant_create(handler, script=script)
            except Exception as e:
                raise

        id_tenant = str(handler.id_tenant)

        if id_tenant not in cls.objects_cache:
            cls.objects_cache[id_tenant] = {}

        if cls.__name__ not in cls.objects_cache[id_tenant]:
            # print('-------- create ',cls.__name__)

            cls.objects_cache[id_tenant][cls.__name__] = await cls._create(handler)
        else:
            # print('++++++++ invlidate',cls.__name__)

            await cls.objects_cache[id_tenant][cls.__name__].invalidate(handler)

        return cls.objects_cache[id_tenant][cls.__name__]

    def __len__(self):
        return self.cache_by_id.__len__()

    def all_by_index(self, index='code', id_only=True):
        if index not in self.cache_by_index:
            return None

        if id_only:
            return self.cache_by_index[index]

        return {x: self.cache_by_id[self.cache_by_index[index][x]] for x in self.cache_by_index[index]}

    @classmethod
    async def _create(cls, handler):

        try:
            result, code = await cls.fetch_method(handler.request, None)  # cls.last_updated)
        except Exception as e:
            raise

        if code != http.status.OK:
            raise NameError('Error fetching lookup')

        cls.last_updated = result['last_updated']
        if cls.last_updated:
            cls.last_updated = dateutil.parser.parse(cls.last_updated)
        if cls.last_updated and tortoise.timezone.is_naive(cls.last_updated):
            cls.last_updated = tortoise.timezone.make_aware(cls.last_updated)

        cls.cache_by_id = result['items']
        for itm in cls.cache_by_id:

            for idx in cls.indexes:
                if idx not in cls.cache_by_index:
                    cls.cache_by_index[idx] = {}

                if type(idx) != str:
                    _idx = ':'.join(idx)
                    v = ':'.join(cls.cache_by_id[itm][idx[x]] for x in range(len(idx)))
                else:
                    v = cls.cache_by_id[itm][idx]

                cls.cache_by_index[idx][v] = itm

        lkp = cls()

        return lkp

    @classmethod
    async def invalidate(cls, handler):

        if not cls.mutable:
            return

        try:
            result, code = await cls.fetch_method(handler.request, cls.last_updated)
        except Exception as e:
            raise
        cls.last_updated = result['last_updated']

        cls.last_updated = dateutil.parser.parse(cls.last_updated) if type(
            cls.last_updated) == str else cls.last_updated
        if cls.last_updated and tortoise.timezone.is_naive(cls.last_updated):
            cls.last_updated = tortoise.timezone.make_aware(cls.last_updated)

        for itm in result['items']:
            # if item['id'] not in cls.cache_by_id:
            cls.cache_by_id[itm] = result['items'][itm]
            for idx in cls.indexes:
                if type(idx) != str:
                    _idx = ':'.join(idx)
                    v = ':'.join(cls.cache_by_id[itm][idx[x]] for x in range(len(idx)))
                else:
                    v = cls.cache_by_id[itm][idx]

                cls.cache_by_index[idx][v] = itm

        # cls.cache_by_id = result['items']
        # for itm in cls.cache_by_id:
        #
        #     for idx in cls.indexes:
        #         if idx not in cls.cache_by_index:
        #             cls.cache_by_index[idx] = {}
        #
        #         if type(idx) != str:
        #             _idx = ':'.join(idx)
        #             v = ':'.join(cls.cache_by_id[itm][idx[x]] for x in range(len(idx)))
        #         else:
        #             v = cls.cache_by_id[itm][idx]
        #
        #         cls.cache_by_index[idx][v] = itm

    def exists(self, key, index='id'):

        if type(key) in (uuid.UUID, asyncpg.pgproto.pgproto.UUID):
            key = str(key)

        if type(key) == uuid.UUID:
            key = str(key)

        if index != 'id':
            if key not in self.cache_by_index[index]:
                return False
            key = self.cache_by_index[index][key]

        return key in self.cache_by_id

    def get(self, key, index='id', default=KeyError, dkey=None):

        if type(key) in (uuid.UUID, asyncpg.pgproto.pgproto.UUID):
            key = str(key)

        if type(key) == uuid.UUID:
            key = str(key)

        if index != 'id':
            key = self.cache_by_index[index][key]

        if key not in self.cache_by_id:
            if default == KeyError:
                raise KeyError

            return default

        res = copy.copy(self.cache_by_id[key])
        if 'id' not in res:
            res['id'] = key

        if not dkey:
            return res

        if dkey in res:
            return res[dkey]

        return default if default is not KeyError else None

        # return self.cache_by_id[key]


class LookupUserGroups(Lookup):
    name = 'user_groups'
    fetch_method = ipc_tenants.lookup_user_groups
    last_updated = None
    indexes = [('group_code', 'code')]
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupUserPermissions(Lookup):
    name = 'user_permissions'
    fetch_method = ipc_tenants.lookup_user_permissions
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupUserRoles(Lookup):
    name = 'user_permissions'
    fetch_method = ipc_tenants.lookup_user_roles
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupTicketTypes(Lookup):
    name = 'ticket_types'

    mutable = False

    fetch_method = ipc_tickets.lookup_ticket_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupUsers(Lookup):
    name = 'users'

    fetch_method = ipc_tenants.lookup_users
    last_updated = None
    indexes = ['unique_id', 'username']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupTenants(Lookup):
    name = 'tenants'

    fetch_method = ipc_tenants.lookup_tenants
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupCountries(Lookup):
    name = 'countries'

    use_tenant = False

    fetch_method = ipc_geoloc.lookup_countries
    last_updated = None
    indexes = ['id']
    cache_by_id = {}
    cache_by_index = {}


class LookupCompanies(Lookup):
    name = 'companies'

    fetch_method = ipc_bp.lookup_companies
    last_updated = None
    indexes = ['number']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupCompanyTypes(Lookup):
    name = 'company_types'

    fetch_method = ipc_bp.lookup_company_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupCompanySites(Lookup):
    name = 'company_sites'

    fetch_method = ipc_bp.lookup_company_sites
    last_updated = None
    indexes = ['number']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupPhoneNumberTypes(Lookup):
    name = 'contacts_phone_number_types'

    mutable = False

    fetch_method = ipc_contacts.lookup_phone_number_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupEmailTypes(Lookup):
    name = 'contacts_email_types'

    mutable = False

    fetch_method = ipc_contacts.lookup_email_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupTicketPriorities(Lookup):
    name = 'ticket_priorities'

    mutable = False

    fetch_method = ipc_tickets.lookup_ticket_priorities
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupTicketStatuses(Lookup):
    name = 'ticket_statuses'

    mutable = False

    fetch_method = ipc_tickets.lookup_ticket_statuses
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupEducationalTitle(Lookup):
    name = 'edu_titles'

    mutable = False

    fetch_method = ipc_bp.lookup_educational_titles
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupGender(Lookup):
    name = 'genders'

    mutable = False

    fetch_method = ipc_bp.lookup_genders
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupNationality(Lookup):
    name = 'nationalities'

    mutable = False

    fetch_method = ipc_bp.lookup_nationalities
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupDocumentType(Lookup):
    name = 'personal_document_types'

    mutable = False

    fetch_method = ipc_bp.lookup_document_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupPhoneType(Lookup):
    name = 'phone_types'

    mutable = False

    fetch_method = ipc_bp.lookup_phone_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupEmailType(Lookup):
    name = 'email_types'

    mutable = False

    fetch_method = ipc_bp.lookup_email_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupFlowTypes(Lookup):
    name = 'flow_types'

    mutable = False

    fetch_method = ipc_flows.lookup_flow_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupWikiStatuses(Lookup):
    name = 'wiki_statuses'

    # ovim smo zatarbili mogucnost da neko doda lookups za wiki status preko frontenda bez potrebe da rezetuje servise.
    mutable = False

    # cmutable ima smisla koristiti kod user rola jer dodavanje user rola / permisija zahteva svakako restart programa zbog implementacije istih

    fetch_method = ipc_wiki.lookup_wiki_statuses
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupSLAGroup(Lookup):
    name = 'sla_group'
    mutable = False
    fetch_method = ipc_sla.lookup_sla_group
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupSLAAdditional(Lookup):
    name = 'sla_additional'
    mutable = False
    fetch_method = ipc_sla.lookup_sla_additional
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupSLAMain(Lookup):
    name = 'sla_main'
    mutable = False
    fetch_method = ipc_sla.lookup_sla_main
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupSLAStatuses(Lookup):
    name = 'sla_statuses'
    mutable = False
    fetch_method = ipc_sla.lookup_status
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupSLABillingPeriod(Lookup):
    name = 'sla_billing_period'
    mutable = False
    fetch_method = ipc_sla.lookup_billing_period
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupSLABusinessComponents(Lookup):
    name = 'sla_business_components'
    mutable = False
    fetch_method = ipc_sla.lookup_sla_business_components
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupSLABusinessComponentGroup(Lookup):
    name = 'business_component_groups'
    mutable = False
    fetch_method = ipc_sla.lookup_sla_business_component_groups
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOpenMessengerType(Lookup):
    name = 'open_messenger_type'

    fetch_method = ipc_open_messenger.lookup_open_messenger_type
    mutable = False
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOpenMessengerStatuses(Lookup):
    name = 'open_messenger_statuses'

    fetch_method = ipc_open_messenger.lookup_open_messenger_statuses
    mutable = False
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupServicesServiceGroups(Lookup):
    name = 'services_service_groups'

    mutable = False

    fetch_method = ipc_services.lookup_services_service_groups
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupServicesServiceTypes(Lookup):
    name = 'services_service_types'

    mutable = False

    fetch_method = ipc_services.lookup_services_service_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupServicesPhoneNumberOrigins(Lookup):
    name = 'services_phone_number_origins'

    mutable = False

    fetch_method = ipc_services.lookup_services_phone_number_origins
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupServicesServiceStatus(Lookup):
    name = 'services_service_status'

    mutable = False

    fetch_method = ipc_services.lookup_services_service_status
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupPdfGeneratorDocumentTypes(Lookup):
    name = 'pdf_generator_document_types'

    mutable = False

    fetch_method = ipc_pdf_generator.lookup_pdf_generator_document_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupServicesSimStatus(Lookup):
    name = 'services_sim_status'

    fetch_method = ipc_services.lookup_services_sim_status
    mutable = False
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupServicesServiceTemplateItemType(Lookup):
    name = 'services_service_template_item_type'

    fetch_method = ipc_services.lookup_services_service_template_item_type
    mutable = False
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupWalletTransactionType(Lookup):
    name = 'wallet_transaction_type'

    mutable = False

    fetch_method = ipc_wallet.lookup_wallet_transaction_type
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupWalletExchangeOperation(Lookup):
    name = 'wallet_exchange_operation'

    mutable = False

    fetch_method = ipc_wallet.lookup_wallet_exchange_operation
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupTenantsPreferedLanguage(Lookup):
    name = 'tenants_prefered_language'

    mutable = False

    fetch_method = ipc_tenants.lookup_tenants_prefered_language
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupFlowVisibility(Lookup):
    name = 'flows_flow_visibility'

    mutable = False

    fetch_method = ipc_flows.lookup_flows_flow_visibility
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupFlowPriorities(Lookup):
    name = 'flows_flow_priorities'

    mutable = False

    fetch_method = ipc_flows.lookup_flows_flow_priorities
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupKanbanKanbanApplication(Lookup):
    name = 'kanban_kanban_application'

    mutable = False

    fetch_method = ipc_kanban.lookup_kanban_kanban_application
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupDealsDealStages(Lookup):
    name = 'deals_deal_stages'

    mutable = False

    fetch_method = ipc_deals.lookup_deals_deal_stages
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupBpIndustryTypes(Lookup):
    name = 'bp_industry_types'

    mutable = False

    fetch_method = ipc_bp.lookup_bp_industry_types
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupDealsDealClassifications(Lookup):
    name = 'deals_deal_classifications'

    mutable = False

    fetch_method = ipc_deals.lookup_deals_deal_classifications
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupBpGenderPrefix(Lookup):
    name = 'bp_gender_prefix'

    mutable = False

    fetch_method = ipc_bp.lookup_bp_gender_prefix
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupDealsDealSources(Lookup):
    name = 'deals_lead_sources'

    mutable = False

    fetch_method = ipc_deals.lookup_deals_deal_sources
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupDealsDealStatuses(Lookup):
    name = 'deals_deal_statuses'

    mutable = False

    fetch_method = ipc_deals.lookup_deals_deal_statuses
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupMessengerChatNotificationChannel(Lookup):
    name = 'messenger_chat_notification_channel'

    mutable = False

    fetch_method = ipc_messenger.lookup_messenger_chat_notification_channel
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloProcess(Lookup):
    name = 'olo_olo_process'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_process
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloOperator(Lookup):
    name = 'olo_olo_operator'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_operator
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloOperationGroup(Lookup):
    name = 'olo_olo_operation_group'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_operation_group
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloOperationType(Lookup):
    name = 'olo_olo_operation_type'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_operation_type
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloOperationStatus(Lookup):
    name = 'olo_olo_operation_status'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_operation_status
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloOperationSteps(Lookup):
    name = 'olo_olo_operation_steps'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_operation_steps
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupConferencesConfSessionStatus(Lookup):
    name = 'conferences_conf_session_status'

    mutable = False

    fetch_method = ipc_conferences.lookup_conferences_conf_session_status
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloDirection(Lookup):
    name = 'olo_olo_direction'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_direction
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass


class LookupOloOloInterface(Lookup):
    name = 'olo_olo_interface'

    mutable = False

    fetch_method = ipc_olo.lookup_olo_olo_interface
    last_updated = None
    indexes = ['code']
    cache_by_id = {}
    cache_by_index = {}

    def __init__(self):
        pass

# {{ lookup }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
