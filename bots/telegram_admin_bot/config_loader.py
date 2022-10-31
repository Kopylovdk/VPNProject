import yaml

with open(f'config.yaml', 'r', encoding='utf8') as stream:
    CONFIG = yaml.safe_load(stream)
