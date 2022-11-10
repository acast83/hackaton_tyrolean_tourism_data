#!../.venv/bin/python3
import os
import sys
import click

from base3.utils import load_config
from scripts.load_env_variables import load_env_variables

current_file_folder = os.path.dirname(os.path.realpath(__file__))

allowed_aerich_commands = (
    "downgrade", "heads", "history",  # "init",
    "init-db", "inspectdb", "migrate", "upgrade",
)


@click.command()
@click.option('--command', '-c', type=click.Choice(['init-db', 'upgrade', 'migrate', 'reset', 'clean-and-reset', 'recreate-db','aerich-init'], case_sensitive=False))
@click.option('--services', '-s', multiple=True, default=None)
@click.option('--installation', '-i', multiple=False, default=None)
@click.option('--host', '-h', multiple=False, default=None)
@click.option('--username', '-U', multiple=False, default=None)
@click.option('--password', '-p', multiple=False, default=None)
@click.option('--yes', '-y', multiple=False, default=None, is_flag=True)
def main(command: str, services: tuple = None, installation=None, host = None, username = None, password = None, yes = None):

    if not command:
        print('missing command, try --help')
        sys.exit()

    installation = f'.{installation}' if installation else ''

    if not services and not yes:
        if input("run aerich for all services (Y)").lower().strip() not in ('', 'yes', 'y'):
            print("nothing has been done")
            sys.exit(0)
    elif len(services) == 1:
        services = services[0].split(',')
    else:
        services = list(services)

    load_env_variables(from_config_file=f'environments/environment{installation}.yaml',
                       config_file_sections=['monolith'],
                       )

    config = load_config('/', [current_file_folder + f'/config/db{installation}.yaml'])

    svc_config = load_config('/', [current_file_folder + f'/config/services{installation}.yaml'])
    active_services = [s for s in svc_config['services'] if svc_config['services'][s]['active']]

    if not services:
        services = active_services
    else:
        services = [s for s in services if s in active_services]

    
    print("performing ",command,'to',services)

    host = host if host else os.getenv('PG_HOST')
    username = username if username else os.getenv('PG_USER')
    password = password if password else os.getenv('PG_PASSWORD')

    print(f'using database: {username}:{password}@{host}')

    
    os.environ['PG_HOST'] = host
    os.environ['PG_USER'] = username
    os.environ['PG_PASSWORD'] = password

    pfx = os.getenv('installation_name','impresaone')

    if command == 'recreate-db':
    
        cmd = f'''PGPASSWORD={password} psql -h {host} -U {username} template1 -c "drop database if exists {pfx}_aerich" -c "create database {pfx}_aerich"'''
        os.system(cmd)
        for app in services:
            cmd = f'''PGPASSWORD={password} psql -h {host} -U {username} template1 -c "drop database if exists {pfx}_{app}" -c "create database {pfx}_{app}"'''
            os.system(cmd)
        
        sys.exit()
        
    if command in ('aerich-init',):
        cmd = 'aerich --app=aerich init-db'
        os.system(cmd)
        sys.exit()
        
    if command in ('reset','clean-and-reset'):
    
        if command=='clean-and-reset' and len(services)>1:
            print("ERROR, clean-and-reset can use only with 1 service")
            return
    

        cmd = f'''PGPASSWORD={password} psql -h {host} -U {username} template1 -c "create database {pfx}_aerich"'''
        os.system(cmd)
        cmd = f'aerich --app=aerich upgrade'
        os.system(cmd)
            
        for app in services:
            cmd = f'''PGPASSWORD={password} psql -h {host} -U {username} {pfx}_aerich -c "delete from aerich where app='{app}';"'''
            os.system(cmd)
            cmd = f'''PGPASSWORD={password} psql -h {host} -U {username} {pfx}_aerich -c "drop database {pfx}_{app}" -c "create database {pfx}_{app}";'''
            os.system(cmd)
                
            if command == 'reset':
                cmd = f'aerich --app={app} upgrade'
                os.system(cmd)
            elif command == 'clean-and-reset':
                cmd = f'''rm -rf migrations/{app}'''
                os.system(cmd)
                cmd = f'aerich --app={app} init-db'
                os.system(cmd)
             
        sys.exit()

    cmd = f'aerich --app=aerich upgrade'
    os.system(cmd)
    for app in services:
        cmd = f'aerich --app={app} {command}'

        print("CMD",cmd)
        os.system(cmd)


    # print(f"using database: {os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}")
    # sys.exit()
    #
    # svc = None
    # if len(sys.argv) == 3:
    #     svc = sys.argv[2]
    #
    # if len(sys.argv) >= 2:
    #     for app in config['tortoise']['apps']:
    #         if svc and app != svc:
    #             continue
    #
    #         print(app)
    #         command = sys.argv[1]
    #         if command in allowed_aerich_commands:
    #             cmd = f'aerich --app={app} {sys.argv[1]}'
    #             print("CMD", cmd)
    #             os.system(cmd)
    #         else:
    #             raise ValueError(f"Command should be one of: {allowed_aerich_commands}.\n"
    #                              f"But '{sys.argv[1]}' is supplied.")
    # else:
    #     raise Exception(f"{sys.argv[0]} gets exactly one argument but {len(sys.argv) - 1} supplied.")


if __name__ == '__main__':
    main()
