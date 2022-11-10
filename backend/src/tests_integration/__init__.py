from scripts.load_env_variables import load_env_variables

try:
    load_env_variables(from_config_file='../environments/environment.yaml',
                       config_file_sections=['testing'],
                       )
except:
    load_env_variables(from_config_file='environments/environment.yaml',
                       config_file_sections=['testing'],
                       )
