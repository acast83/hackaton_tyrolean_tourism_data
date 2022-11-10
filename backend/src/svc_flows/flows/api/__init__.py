import os
import base3.decorators
from base3.utils import load_config

svc_name = 'flows'
import base3.test as b3t

current_file_folder = os.path.dirname(os.path.realpath(__file__))
cfg = load_config('/', [current_file_folder + '/../../../config/services.yaml'])
config = cfg['services'][svc_name]
base3.decorators.route.set('prefix', config['prefix'])
base3.decorators.route.set('service_name', svc_name)

dbconfig = load_config('/', [current_file_folder + '/../../../config/db.yaml'])


def get_db_connection():
    if b3t.test_mode:
        return 'conn_test'

    return dbconfig['tortoise']['apps'][svc_name]['default_connection']


from .flows import *
from .lookups import *
