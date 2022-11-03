import yaml
# PROD
# config_file_name = 'config.yaml'
# TEST
config_file_name = 'config_test.yaml'

with open(f'configs/{config_file_name}', 'r', encoding='utf8') as stream:
    CONFIG = yaml.safe_load(stream)

