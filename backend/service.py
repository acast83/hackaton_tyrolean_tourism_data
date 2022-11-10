#!../.venv/bin/python 

import os
from subprocess import Popen

from base3.utils import load_config

from scripts.load_env_variables import load_env_variables


current_file_folder = os.path.dirname(os.path.realpath(__file__))

load_env_variables(from_config_file='environments/environment.yaml',
                   config_file_sections=['microservices'],
                   )

from tshared_src.tshared.utils.processes_health_checker import *    # noqa


def start_up_workers(wconfig: dict) -> list[Popen]:     # noqa
    """
    sim-cards-info-db-updater:
      command: python workers/plintron_csv.py
      scale: 1
      queue: plintron_new_csv_upload
    """

    _started_workers = []
    
    for worker_name, worker_config in wconfig.items():
        try:
            command_ = worker_config['command']
            scale = int(worker_config.get('scale', 1))

            for _ in range(scale):
                _started_worker = create_process(command_.split())
                _started_workers.append(_started_worker)

        except Exception as e:      # noqa
            pass
    
    return _started_workers


if __name__ == "__main__":

    os.system('/usr/sbin/service cron start')
    os.system('/usr/bin/crontab /app/config/cron.txt')
    os.system('rm -rf /var/log/impresaone && ln  -sf /tmp/impresaone/logs /var/log/impresaone')

    config = load_config(current_file_folder + '/config', ['services.yaml'])

    by_port = {}
    for svc in config['services']:
        port = int(config['services'][svc]['port'])
        if port not in by_port:
            by_port[port] = []

        by_port[port].append(svc)

    upstreams = []
    locations = []
    rewrites = []
    started_services = []

    for port in by_port:

        for svc in by_port[port]:
            upstreams.append(f'upstream {svc} {{ ip_hash; server localhost:{port} max_fails=3  fail_timeout=600s; }}')

            locations.append(f'location /api/v3/{svc} {{ resolver 8.8.8.8; proxy_pass http://{svc};   '
                             f'proxy_redirect off; proxy_set_header Host $host; '
                             f'proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For '
                             f'$remote_addr; }}')
            rewrites.append(f'rewrite ^/api/v3/{svc}/(.*)$ /api/v3/{svc}/$1 break;')

        command = 'python monolith_service_args.py {}'.format(' '.join([f'-s {x}' for x in by_port[port]]))

        started_service = create_process(command.split())
        started_services.append(started_service)

    upstreams = '\n'.join(upstreams)
    locations = '\n'.join(locations)
    rewrites = '\n'.join(rewrites)

    nginx = f'''{upstreams}

server {{

        listen 80 default_server;
        listen [::]:80 default_server;

        root /tmp;
        index index.html;

    server_name _;

    client_max_body_size 100M;
    proxy_connect_timeout       600;
    proxy_send_timeout          600;
    proxy_read_timeout          600;
    send_timeout                600;

{locations}
    proxy_buffering off;

{rewrites}

    rewrite ^/(.*)$ /$1 break;


}}'''

    with open('/etc/nginx/sites-available/default', 'wt') as f:
        f.write(nginx)

    os.system('service nginx restart')

    wconfig = config.get('workers', {})
    started_workers = start_up_workers(wconfig=wconfig)

    started_processes = started_services + started_workers

    run_processes_health_check(processes=started_processes,
                               health_check_period=10,
                               )
