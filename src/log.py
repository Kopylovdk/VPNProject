import typing
from pathlib import Path


def deep_update_dict(d: dict, f: typing.Callable[[typing.Any, typing.Any], typing.Any]) -> None:
    for k, v in d.items():
        if isinstance(v, dict):
            deep_update_dict(v, f)
        elif isinstance(v, list):
            for item in v:
                if isinstance(v, dict):
                    deep_update_dict(item, f)
        else:
            d[k] = f(k, v)


def logging_config_update(config: dict, log_path: typing.Union[str, Path]) -> dict:
    log_path = Path(log_path)
    deep_update_dict(config, lambda k, v: log_path / Path(v) if k == 'filename' else v)
    return config
