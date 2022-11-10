from tortoise import fields, Model
import tshared.models.base as base_models
import tortoise.signals


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "geoloc_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'geoloc'


class Country(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_countries"
        app = 'geoloc'

    serialization_fields_order = ('id', 'en_value', 'local_value')
    default_fields = ('id', 'en_value', 'local_value', 'translation', 'code')

    name_case_fields = {'en_value', 'local_value', 'translation'}

    connected_fields = {
        'translation': 'translations.value'
    }

    allowed_ordering = {
        'en_value': 'en_value',
        'local_value': 'local_value',
    }

    code = fields.CharField(max_length=32, null=False, unique=True)
    en_value = fields.CharField(max_length=128, null=False, unique=True)
    local_value = fields.CharField(max_length=128, null=False, unique=True)

    eu_country = fields.BooleanField(null=True)


class TranslationCountry(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_translations_countries"
        app = 'geoloc'

    country = fields.ForeignKeyField('geoloc.Country', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)
    cs_value = fields.TextField(null=True)  # case sensetive value


class Region(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_regions"
        app = 'geoloc'
        unique_together = (('country', 'local_value'),)

    country = fields.ForeignKeyField('geoloc.Country', null=False, index=True, related_name='regions')
    local_value = fields.CharField(max_length=128, null=False)
    cs_value = fields.CharField(max_length=128, null=True)
    en_value = fields.CharField(max_length=128, null=True, )

    serialization_fields_order = ('id', 'local_value')
    default_fields = ('id', 'local_value', 'en_value')

    name_case_fields = {'local_value', 'translation'}

    connected_fields = {
        'translation': 'translations.value'
    }

    allowed_ordering = {
        'local_value': 'local_value',
    }


class TranslationRegion(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_translations_regions"
        app = 'geoloc'

    region = fields.ForeignKeyField('geoloc.Region', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)
    cs_value = fields.TextField(null=True)


class Province(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_provinces"
        app = 'geoloc'
        unique_together = (('country', 'local_value'),
                           ('country', 'code'),
                           ('region', 'local_value'))

    country = fields.ForeignKeyField('geoloc.Country', null=False, index=True, related_name='provinces')
    region = fields.ForeignKeyField('geoloc.Region', null=True, index=True, related_name='provinces')

    local_value = fields.CharField(max_length=128, null=False)
    cs_value = fields.CharField(max_length=128, null=True)
    en_value = fields.CharField(max_length=128, null=True, )

    code = fields.CharField(max_length=32, null=True)

    serialization_fields_order = ('id', 'province_id', 'local_value')
    default_fields = ('id', 'province_id', 'local_value', 'en_value')

    name_case_fields = {'local_value', 'translation'}

    connected_fields = {
        'translation': 'translations.value'
    }

    allowed_ordering = {
        'local_value': 'local_value',
    }


class TranslationProvince(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_translations_provinces"
        app = 'geoloc'

    province = fields.ForeignKeyField('geoloc.Province', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)
    cs_value = fields.TextField(null=True)


class Municipality(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_municipalities"
        app = 'geoloc'
        unique_together = (('country', 'zip', 'local_value'),
                           ('region', 'zip', 'local_value'),
                           ('province', 'zip', 'local_value'))

    country = fields.ForeignKeyField('geoloc.Country', null=False, index=True, related_name='municipalities')
    region = fields.ForeignKeyField('geoloc.Region', null=True, index=True, related_name='municipalities')
    province = fields.ForeignKeyField('geoloc.Province', null=True, index=True, related_name='municipalities')

    zip = fields.CharField(max_length=32, null=True, index=True)

    istat_code = fields.CharField(max_length=32, null=True, index=True)

    local_value = fields.CharField(max_length=128, null=False)
    cs_value = fields.CharField(max_length=128, null=True)
    en_value = fields.CharField(max_length=128, null=True, )

    serialization_fields_order = ('id', 'region_id', 'province_id', 'zip', 'local_value', 'istat_code')
    default_fields = ('id', 'zip', 'local_value', 'en_value', 'istat_code', 'translation', 'country_id', 'province_id')

    name_case_fields = {'local_value', 'translation'}

    connected_fields = {
        'translation': 'translations.value'
    }

    allowed_ordering = {
        'local_value': 'local_value',
    }


class MunicipalitySearch(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_municipalities_search"
        app = 'geoloc'

    # on creation we will split city name to workds, ignor "in, the, " and for one city
    # add mulitply entries in this table

    # all searches should be with filter starts_with

    municipality = fields.ForeignKeyField('geoloc.Municipality', null=False, index=True, related_name='search')
    language = fields.CharField(max_length=32, null=False)

    #alway lowercase
    value = fields.TextField(null=False)                    # will be just one word



class TranslationMunicipality(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "geoloc_translations_municipalities"
        app = 'geoloc'

    municipality = fields.ForeignKeyField('geoloc.Municipality', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)
    cs_value = fields.TextField(null=True)


@tortoise.signals.pre_save(Region)
async def region_pre_save(sender: "Type[Region]", instance: Region, using_db, update_fields):
    return await base_models.fix_name_case_fields(instance)


@tortoise.signals.pre_save(Country)
async def country_pre_save(sender: "Type[Country]", instance: Country, using_db, update_fields):
    return await base_models.fix_name_case_fields(instance)


@tortoise.signals.pre_save(Province)
async def province_pre_save(sender: "Type[Province]", instance: Province, using_db, update_fields):
    return await base_models.fix_name_case_fields(instance)


@tortoise.signals.pre_save(Municipality)
async def municipality_pre_save(sender: "Type[Municipality]", instance: Municipality, using_db, update_fields):
    return await base_models.fix_name_case_fields(instance)