#!/usr/bin/env python
import pathlib
import click

from sources.process_template import process_template
from sources.process_shared_files import process_shared_files
from sources.process_lookups import process_lookups
from utils import read_yaml_config, get_directories, check_variables_placeholders
from sources.template_tests_integration import template_test_integration


@click.command()
@click.option("-n", "--name", required=True,
              help='New service name.')
@click.option("-t", "--template", default=None, show_default=True,
              help='Name of tar-archive template.')
@click.option("-l", "--lookups", default=None, show_default=True,
              help='JSON-file with lookups.')
@click.option("-c", "--config", default=None, show_default=True,
              help='Yaml-file consisting paths to files and directories')
@click.option("--test_mode", is_flag=True,
              help='If supplied changes will be applied to copies of project files.')
def main(name, template, lookups, config, test_mode):
    """ Script for creating base3 microservice.

    Template compressed using following command: tar -zcvf mmm.tar.gz svc_mmm
    """

    script_location = pathlib.Path(__file__).parent

    if config is None:
        config = read_yaml_config(config_path=pathlib.Path(script_location, 'config.yaml').resolve(strict=True))
    else:
        config = read_yaml_config(config_path=pathlib.Path(pathlib.Path.cwd(), config))
    services_location = pathlib.Path(script_location, config['services_location']).resolve(strict=True)

    if template is None:
        template = pathlib.Path(script_location, 'templates/mmm.tar.gz').resolve(strict=True)
    else:
        if pathlib.Path(template).is_dir():
            template = pathlib.Path(pathlib.Path.cwd(), 'mmm.tar.gz').resolve(strict=True)
        else:
            template = pathlib.Path(pathlib.Path.cwd(), template).resolve(strict=True)

    dirs = get_directories(service_name=name, config=config, is_test_mode=test_mode)

    process_template(template=template, new_svc_name=name,
                     services_location=services_location, script_location=script_location)
    process_shared_files(service_name=name,
                         directories=dirs)
    template_test_integration(service_name=name, lookup_name='',
                              template_path=dirs['test_integration']['template'],
                              target_file=dirs['test_integration']['target'])

    if lookups is not None:
        check = check_variables_placeholders(dirs=dirs, service_name=name, services_location=services_location)
        if check:
            lookups = pathlib.Path(pathlib.Path.cwd(), lookups).resolve(strict=True)
            process_lookups(service_name=name, lookups=lookups, dirs=dirs, services_location=services_location)


if __name__ == "__main__":
    main()
