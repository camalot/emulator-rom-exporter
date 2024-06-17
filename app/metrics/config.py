import codecs
import json
import os

import yaml
from libs.utils import dict_get


class EmulatorRomMetricsConfig:
    APP_VERSION = "1.0.0-snapshot"
    def __init__(self, file: str):
        # set defaults for config from environment variables if they exist
        self.metrics = {
            "port": int(dict_get(os.environ, "ERE_CONFIG_METRICS_PORT", "8932")),
            "pollingInterval": int(dict_get(os.environ, "ERE_CONFIG_METRICS_POLLING_INTERVAL", "86400")),
        }
        self.version = self.APP_VERSION
        self.include_empty = bool(dict_get(os.environ, "ERE_CONFIG_INCLUDE_EMPTY", "true"))
        self.log_level = dict_get(os.environ, "ERE_LOG_LEVEL", "DEBUG")
        self.emulators = []
        try:
            # load app/data/emulators.yaml
            defaults_file = "./data/emulators.yaml"
            if os.path.exists(defaults_file):
                with codecs.open(defaults_file, encoding="utf-8-sig", mode="r") as f:
                    settings = yaml.safe_load(f)
                    self.__dict__.update(settings)
                    print(json.dumps(self.__dict__))
            # check if file exists
            if os.path.exists(file):
                with codecs.open(file, encoding="utf-8-sig", mode="r") as f:
                    settings = yaml.safe_load(f)
                    # if settings["emulators"], merge with defaults
                    if settings["emulators"]:
                        defaults = set(self.__dict__["emulators"])
                        user = set(settings["emulators"])
                        new = defaults.union(user)
                        list(self.__dict__["emulators"]).extend(list(new))
                    # remove emulators key
                    del settings["emulators"]
                    # update the rest of the settings
                    self.__dict__.update(settings)
        except yaml.YAMLError as exc:
            raise exc
