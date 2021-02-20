from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader  # type: ignore


def load_yaml(yaml_string: str):
    data = load(yaml_string, Loader=Loader)
    return data
