import uuid
import json
import bcrypt
import base3.handlers
from base3 import http
from base3.core import Base
from base3.decorators import route, api

from tortoise.transactions import in_transaction

from .. import models
import tortoise.timezone
import datetime

from . import config, app_config
import tshared.ipc.sendmail as ipc_sendmail
import tshared.ipc.sms as ipc_sms
import tshared.ipc.tenants

import tshared.ipc.flows as ipc_flows
import tshared.lookups
import random

import tshared.utils.common as common
import os

@route('/pydantic_test')
class PYDanticXTenantsHandler(base3.handlers.Base):
    @api(auth=False)
    async def get(self):

        from tortoise.contrib.pydantic import pydantic_model_creator

        u = pydantic_model_creator(models.User)

        u.id = uuid.uuid4()
        u.created = datetime.datetime.now()
        u.pera = 'zika'
        u.email = 'igor@digitalcube.rs'

        print(u)

        return {}

        return json.loads(u.schema_json())
