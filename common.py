import yaml

__config = None


def config():
    if not __config:
        with open('config.yaml') as f:
            config = yaml.full_load(f)

    return config
