import os

import yaml

_external_configs = None
EXTERNAL_CONFIG_PATH = os.getenv('OUT_PATH_CONF', '')


def get_external_configs():
    global _external_configs

    if _external_configs is not None:
        return _external_configs

    conf_path = os.path.join(EXTERNAL_CONFIG_PATH, 'config.yaml')

    with open(conf_path, 'r', encoding='utf8') as stream:
        _external_configs = yaml.safe_load(stream)

    return _external_configs
