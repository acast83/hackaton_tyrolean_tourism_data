import os
import re
import yaml
import copy

_env_var_pattern = re.compile(r'.*?\${(\w+)}.*?')


def load_config(config_folder: str, cfg_files: list):



    if type(cfg_files) == str:
        cfg_files = [cfg_files]

    cfg_files = [os.path.abspath(config_folder+'/'+f) for f in cfg_files]

    if hasattr(load_config, 'cache') and str(cfg_files) in load_config.cache:

#        print("LOAD CONFIG (cached)")

        return copy.deepcopy(load_config.cache[str(cfg_files)])

    
#    print("LOAD CONFIG (first) : API_PREFIX=", os.getenv('API_PREFIX'))


    def fix_db_params(cfg):
        if 'db' not in cfg:
            return

        db = cfg['db']

        for key in cfg.keys():
            if key[:3] == 'db_':
                for _k in ('host', 'port', 'user', 'password'):
                    if _k not in cfg[key]:
                        cfg[key][_k] = db[_k]

    def replace_env_variables(dct):
        global _env_var_pattern

        for key in dct.keys():
            val = dct[key]
            if type(val) == dict:
                replace_env_variables(val)
            elif type(val) == str:
                match = _env_var_pattern.findall(val)
                for p in match:
                    dct[key] = val.replace(f'${{{p}}}', os.getenv(p, p))

    def merge_config_files_and_inherit_or_replace_value(from_source, to_destination):
        for key in from_source:
            if key not in to_destination:
                to_destination[key] = from_source[key]
            else:
                if type(from_source[key]) == dict:
                    merge_config_files_and_inherit_or_replace_value(from_source[key], to_destination[key])
                else:
                    to_destination[key] = from_source[key]

    config = {}

    for cfg_file in cfg_files:
        with open(cfg_file) as f:
            _sconfig = yaml.load(f, Loader=yaml.FullLoader)

        merge_config_files_and_inherit_or_replace_value(_sconfig, config)

    replace_env_variables(config)
    fix_db_params(config)

    if not hasattr(load_config, 'cache'):
        load_config.cache = {}

    load_config.cache[str(cfg_files)] = copy.deepcopy(config)

    return config
