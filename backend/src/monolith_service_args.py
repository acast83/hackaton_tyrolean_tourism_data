#!../.venv/bin/python
import os
from typing import Union, Optional
import importlib
from copy import deepcopy
import redis

from tortoise import Tortoise
import click

import base3.app
import base3.decorators
from base3.utils import load_config

from tshared.utils.common import is_port_from_reserved_range, suggest_port
from tshared.utils.setup_logger import setup_logging, log
from tshared.utils.get_redis_instance import get_redis_instance
from scripts.load_env_variables import load_env_variables


config: Optional[dict] = None

current_file_folder = os.path.dirname(os.path.realpath(__file__))


def db_init_factory(services: list):
    async def _db_init():
        config_db = load_config(current_file_folder + '/config', ['db.yaml'])

        tconfig = deepcopy(config_db['tortoise'])

        tconfig['apps'] = {
            service_name: tconfig['apps'][service_name]
            for service_name in services
        }
        tconfig['connections'] = {
            f"conn_{service_name}": tconfig['connections'][f'conn_{service_name}']
            for service_name in services
        }

        if 'aerich' in tconfig['apps']:
            del tconfig['apps']['aerich']

        await Tortoise.init(config=tconfig)

    return _db_init


def run_services(services: Union[list, str], port: int):
    if isinstance(services, str):
        services = [services]

    if config.get('logging'):
        setup_logging(config, services=services)

    for svc in services:
        importlib.import_module(f'svc_{svc}.{svc}.api')

    db_init = db_init_factory(services)
    installation_name = os.getenv('installation_name', 'thilo')

    try:
        log('services').info(f"{installation_name.capitalize()} started")
        base3.app.run(pre_run_async_methods=[db_init],
                      app_name=f"{installation_name}: {', '.join(services)}",
                      port=port)
    except OSError as e:
        log('services').error(str(e))
        raise e
    except KeyboardInterrupt:
        log('services').info(f"{installation_name.capitalize()} stopped")


# https://www.rfc-editor.org/rfc/rfc1700.html
# https://stackoverflow.com/questions/218839/assigning-tcp-ip-ports-for-in-house-application-use
MIN_PORT = 1024
MAX_PORT = 49151


@click.command()
@click.option('--service', '-s', multiple=True, default=None)
@click.option('--port', '-p', type=click.IntRange(MIN_PORT, MAX_PORT), default=None)
@click.option('--installation', '-i', multiple=False, default=None)
def main(service: tuple = None, port: int = None, installation=None):
    """
    Arguments:
        service:
        port:
        installation:
    """

    installation = f'.{installation}' if installation else ''

    load_env_variables(
        from_config_file=f'environments/environment{installation}.yaml',
        config_file_sections=['monolith']
    )

    global config

    config = load_config(
        current_file_folder + '/config', [f'services{installation}.yaml']
    )

    # checking port
    if port and is_port_from_reserved_range(port):
        raise ValueError(f"Port {port} is from reserved ports range "
                         f"please choose another port.\n"
                         f"Suggested port: {suggest_port(port)}")

    # monolith
    if not service:
        active_services = [
            service_name
            for service_name, service_config in config['services'].items()
            if service_config.get('active')
        ]

        port = int(config["application"]["port"]) if not port else port
    else:
        active_services = []
        port = int(config['services'][service[0]]['port']) if not port else port

        host = 'localhost'

        try:
            host = config['application']['docker_host']
        except KeyError:
            pass

        for service in service:
            if service not in config['services']:
                raise ValueError(
                    f'Configuration for service "{service}" not found in "services.yaml"'
                )
            active_services.append(service)

            # r = redis.Redis(host='redis')
            r = get_redis_instance()

            r.set(f'v3_services_host_{service}', host)

    run_services(services=active_services, port=port)


if __name__ == "__main__":
    main()
