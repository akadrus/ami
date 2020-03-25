import yaml


class ConfigLoader:
    @staticmethod
    def load_config(config_path):
        with open(config_path, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                return config
            except yaml.YAMLError as exc:
                print(exc)
                raise
