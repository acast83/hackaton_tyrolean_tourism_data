import os
import yaml
from base3.utils import load_config

current_file_folder = os.path.dirname(os.path.realpath(__file__))
TORTOISE_ORM = load_config(current_file_folder, 'db.yaml')['tortoise']


