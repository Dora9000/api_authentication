
from __future__ import print_function
import pathlib
from copy import deepcopy
import yaml

BASE_DIR = pathlib.Path(__file__).parent
CONFIG_PATH = BASE_DIR / 'config' / 'config.yaml'


def get_config(path):
    with open(path) as file:
        config = yaml.full_load(file)
        return config


def get_secure_config(config):
    config = deepcopy(config)
    return config


def test_config(config):
    """s = config['partially_completed']['lower_bound']
    s = config['partially_completed']['upper_bound']
    s = config['request_timeout']
    s = config['server_request_timeout']
    s = config['urlinventory_api']
    s = config['token_check_url']
    s = config['status_file']['path']
    path_exists(s)
    s = config['status_file']['sleep_time_update']
    s = config['status_file']['sleep_time_clear_dir']
    s = config['all_acc_perm']['url']
    s = config['all_acc_perm']['data']
    s = config['datafile']
    file_exists(s)"""
    return
