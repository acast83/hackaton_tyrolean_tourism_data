#!/usr/bin/env python

import os
import csv
import sys
import json
import anyio
import asyncclick as click
import base64
import random
import asyncio
from base3 import http
from base3.utils import load_config
from scripts.load_env_variables import load_env_variables
import logging

current_file_folder = os.path.dirname(os.path.realpath(__file__))

import tshared.utils.ipc as ipc
import tshared.utils.send_telegram_message as telegram

current_file_folder = os.path.dirname(os.path.realpath(__file__))
config, id_tenant, token, prefix, id_user = None, None, None, None, None


async def check_service(service_name):
    url = prefix + f'/{service_name}/about'
    try:
        res = await ipc.api(None, 'GET', url)
        return res['service'] == service_name
    except:
        return False


async def get_or_create_master_user():
    res = await check_service('tenants')
    if not res:
        print("tenants service not working properly")
        sys.exit()

    try:
        url = prefix + f'/tenants/00000000-0000-0000-0000-000000000000/sessions'
        res = (
            await ipc.api(None, 'POST', url,
                          body={'username': 'master', 'password': 'admin123'},
                          expected_result=None
                          # expected_result=http.status.CREATED

                          ))
        return res['token']
    except Exception as e:

        try:
            res = (await ipc.api(None, 'POST', prefix + '/tenants/users',
                                 {'username': 'master', 'password': 'admin123', 'first_name': 'master',
                                  'last_name': 'user'},
                                 expected_code=http.status.CREATED))

            return res['token']
        except Exception as e:
            print("ERROR CREATEING MASTER USER")
            print(e)
            sys.exit()


async def get_tenant_and_token(code='DCUBE', force_id=None, force_name='Digital CUBE', init_users=None):
    global prefix

    if not await check_service('tenants'):
        print("tenants service not available")
        sys.exit()

    url = prefix + f'/tenants/code/{code}'

    try:
        res = await ipc.api(None, 'GET', url)
    except Exception as e:
        res = {}

    if 'id' in res:
        id_tenant = res['id']
        token = (await ipc.api(None, 'POST', prefix + f'/tenants/{id_tenant}/sessions',
                               {'username': 'system', 'password': '123'},
                               expected_code=http.status.OK))['token']

        return id_tenant, token

    master_user_token = await get_or_create_master_user()

    body = {'code': code}
    if force_id:
        body['id'] = force_id
    if force_name:
        body['name'] = force_name

    id_tenant = (await ipc.api(master_user_token, 'POST', prefix + f'/tenants', body=body))['id']

    res = (await ipc.api(master_user_token, 'POST', prefix + f'/tenants/{id_tenant}/users',
                         body={'username': 'system', 'password': '123'},
                         expected_result=http.status.CREATED))

    token, _id_user = res['token'], res['id']

    return id_tenant, token


async def cfg(installation=''):
    installation = f'.{installation}' if installation else ''
    global id_tenant, token, prefix, config

#    print("CFG")

    config = load_config(current_file_folder + '/../config', [f'services{installation}.yaml'])

#    print(config)

    prefix = f'http://localhost:{config["application"]["port"]}{config["application"]["prefix"]}'

    print("PREFIX", prefix)


async def seed_options(svcs):
    global config

    tenant = os.getenv('INSTALLATION', None)
    if not tenant:
        sys.exit('TENANT not defined in env')

    services = config['services']
    for service in services:

        if svcs and service not in svcs:
            continue

        if 'active' not in services[service] or not services[service]['active']:
            print('skipping', 'active=false')
            continue

        try:
            with open(current_file_folder + f'/../svc_{service}/init/options.{tenant}.json') as f:
                options_tenant_source_json = json.load(f)
        except Exception as e:
            # print('skipping', 'error_occurred', e, 'in svc', service)
            continue
        if not options_tenant_source_json:
            print('skipping', 'no-lookup', service)
            continue

        url = prefix + f'/{service}/options'

        for key in options_tenant_source_json:
            body = {'key': key, 'value': options_tenant_source_json[key]}
            print("TODO", 'POST', url, body)
            res = await ipc.api(token, 'POST', url, body=body)
            print("RES", res)

        # try:
        #     res = await ipc.api(token, 'POST', url, {'lookups': lookups_tenant_source_json})
        #     print("SUCCESSFULLY", url)
        # except Exception as e:
        #     print("-" * 100)
        #     print("SKIPPING", service, url, token[:10] + '...')
        #     print(f'exception {e}')
        #     # sys.exit()


async def seed_lookups(svcs):
    global config

    tenant = os.getenv('INSTALLATION', None)
    if not tenant:
        sys.exit('TENANT not defined in env')

    services = config['services']
    for service in services:

        if svcs and service not in svcs:
            continue

        if 'active' not in services[service] or not services[service]['active']:
            print('skipping', 'active=false')
            continue

        try:
            with open(current_file_folder + f'/../svc_{service}/init/lookups.{tenant}.json') as f:
                lookups_tenant_source_json = json.load(f)
        except Exception as e:
            try:
                with open(current_file_folder + f'/../svc_{service}/init/lookups.json') as f:
                    lookups_tenant_source_json = json.load(f)
            except Exception as e:
                print('1','skipping', 'error_occurred', e, 'in svc', service)
                continue

        if not lookups_tenant_source_json:
            print('2','skipping', 'no-lookup', service)
            continue

        url = prefix + f'/{service}/lookups/init'

        # if service in ('tenants',):
        #     await ipc.api(token, 'POST', prefix + f'/{service}/log/level', {'level': 'DEBUG'})

        try:
            res = await ipc.api(token, 'POST', url, {'lookups': lookups_tenant_source_json})
            print("SUCCESSFULLY", url)
        except Exception as e:
            print("-" * 100)
            print("SKIPPING", service, url, token[:10] + '...')
            print(f'exception {e}')
            # sys.exit()




@click.command()
@click.option('--installation', '-i', multiple=False, default=None)
@click.option('--command', '-c', multiple=False, default=None, type=click.Choice(['lookups', 'init', 'options']))
@click.option('--service', '-s', multiple=True, default=None)
@click.option('--sim-file', '-f', multiple=False, default=None)
@click.option('--sim-nr-cards', '-n', type=int, multiple=False, default=None)
async def seed(command, service: tuple = None, port: int = None, installation=None, sim_file=None, sim_nr_cards=None):

    file = current_file_folder + f'/../environments/environment.yaml'

    load_env_variables(from_config_file=file, config_file_sections=['monolith'])

    global id_tenant, token, prefix, id_user

    await cfg(installation)

    tenant = os.getenv('INSTALLATION', None)
    if not tenant:
        sys.exit('TENANT not defined in env')

    force_id=None

    id_tenant, token = await get_tenant_and_token(code=tenant.upper(), force_id=force_id)
    print(id_tenant)

    if not command:
        print("use --help")
        sys.exit()

    if command == 'init':
        await seed_lookups(service)

    if command == 'lookups':
        await seed_lookups(service)



if __name__ == '__main__':
    asyncio.run(seed())
