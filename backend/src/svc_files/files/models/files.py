import tshared.models.base as base_models
from tortoise import Model


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "files_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'files'

