import yaml


config_file_name = 'config.yaml'

with open(f'configs/{config_file_name}', 'r', encoding='utf8') as stream:
    CONFIG = yaml.safe_load(stream)

