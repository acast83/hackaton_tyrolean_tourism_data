from sources.template_env import template_env
from sources.template_db_yaml import template_db_yaml
from sources.template_services_yaml import template_services_yaml


def process_shared_files(service_name: str, directories: dict):
    template_db_yaml(service_name=service_name,
                     template_path=directories['db_yaml']['template'],
                     target_file=directories['db_yaml']['target'])
    template_services_yaml(service_name=service_name,
                           template_path=directories['services_yaml']['template'],
                           target_file=directories['services_yaml']['target'])
    template_env(service_name=service_name,
                 target_file=directories['env']['target'])
