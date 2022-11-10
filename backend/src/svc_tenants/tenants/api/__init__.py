import os
import base3.decorators
from base3.utils import load_config

svc_name = 'tenants'

current_file_folder = os.path.dirname(os.path.realpath(__file__))
config = load_config('/', [current_file_folder + '/../../../config/services.yaml'])

app_config = config['application']

config = config['services'][svc_name]
base3.decorators.route.set('prefix', config['prefix'])
base3.decorators.route.set('service_name', svc_name)

from .tenants import *
from .lookups import *
