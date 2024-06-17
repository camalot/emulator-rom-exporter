import inspect
import json
import glob
import os
import time
import traceback

from libs import logger
from libs.enums.loglevel import LogLevel
from libs.utils import dict_get
from prometheus_client import Gauge


class EmulatorRomMetrics:
    def __init__(self, config):
        # get the class name
        _method = inspect.stack()[0][3]
        self._class = self.__class__.__name__
        self._module = os.path.basename(__file__)[:-3]
        self.config = config

        log_level = LogLevel[self.config.log_level.upper()]
        if not log_level:
            log_level = LogLevel.DEBUG
        self.log = logger.Log(log_level)

        self.log.debug(f"{self._module}.{self._class}.{_method}", f"{json.dumps(self.config.__dict__)}")

        self.namespace = "emulatorrom"
        self.polling_interval_seconds = config.metrics["pollingInterval"]

        self.files_size = Gauge(
            namespace=self.namespace,
            name=f"files_size",
            documentation="The size of files in the path",
            labelnames=["emulator", "path", "root_path", "glob"],
        )

        self.files_count = Gauge(
            namespace=self.namespace,
            name=f"files_count",
            documentation="The count of files in the path",
            labelnames=["emulator", "path", "root_path", "glob"],
        )
        # self.sum_tacos = Gauge(
        #     namespace=self.namespace,
        #     name=f"tacos",
        #     documentation="The number of tacos give to users",
        #     labelnames=labels,
        # )

        self.build_info = Gauge(
            namespace=self.namespace,
            name=f"build_info",
            documentation="A metric with a constant '1' value labeled with version",
            labelnames=["version", "ref", "build_date", "sha"],
        )

        self.errors = Gauge(
            namespace=self.namespace,
            name=f"exporter_errors",
            documentation="The number of errors encountered",
            labelnames=["source"],
        )

        ver = dict_get(os.environ, "APP_VERSION", "1.0.0-snapshot")
        ref = dict_get(os.environ, "APP_BUILD_REF", "unknown")
        build_date = dict_get(os.environ, "APP_BUILD_DATE", "unknown")
        sha = dict_get(os.environ, "APP_BUILD_SHA", "unknown")
        self.build_info.labels(version=ver, ref=ref, build_date=build_date, sha=sha).set(1)
        self.log.debug(f"{self._module}.{self._class}.{_method}", f"Metrics initialized")

    def run_metrics_loop(self):
        """Metrics fetching loop"""
        _method = inspect.stack()[1][3]
        try:
            while True:
                self.log.info(f"{self._module}.{self._class}.{_method}", f"Begin metrics fetch")
                self.fetch()
                self.log.info(f"{self._module}.{self._class}.{_method}", f"End metrics fetch")
                self.log.debug(
                    f"{self._module}.{self._class}.{_method}",
                    f"Sleeping for {self.polling_interval_seconds} seconds",
                )
                time.sleep(self.polling_interval_seconds)
        except Exception as ex:
            self.log.error(f"{self._module}.{self._class}.{_method}", str(ex), traceback.format_exc())

    def _fetch_emulator(self, path: str, emulator: dict): # todo: add emulator model instead of dict
        _method = inspect.stack()[1][3]
        try:
            self.log.debug(f"{self._module}.{self._class}.{_method}", f"Fetching metrics for {emulator['name']}=>{path}")
            paths = []
            globs = []

            # if emulator has path add it to the list
            if "path" in emulator:
                paths.append(emulator["path"])
            if "paths" in emulator:
                paths.extend(emulator["paths"])

            # if emulator has globs add it to the list
            if "glob" in emulator:
                globs = [emulator["glob"]]
            if "globs" in emulator:
                globs.extend(emulator["globs"])

            for sub_path in emulator["paths"]:
                # combine path and emulator path
                full_path = os.path.join(path, sub_path)
                self.log.debug(f"{self._module}.{self._class}.{_method}", f"{emulator['name']}=>{full_path}")
                # check if path exists
                if os.path.exists(full_path):
                    for glob_filter in emulator["globs"]:
                        self.log.debug(f"{self._module}.{self._class}.{_method}", f"{emulator['name']}=>{sub_path}=>{glob_filter}")
                        # get the files in the path and subdirectories based on the globs
                        files = glob.glob(os.path.join(full_path, glob_filter), recursive=True)
                        total_files = len(files)
                        total_size = sum(os.path.getsize(f) for f in files if os.path.isfile(f))

                        if total_files > 0 or self.config.include_empty:
                            self.files_size.labels(emulator=emulator["name"], path=sub_path, root_path=path, glob=glob_filter).set(total_size)
                        if total_files > 0 or self.config.include_empty:
                            self.files_count.labels(emulator=emulator["name"], path=sub_path, root_path=path, glob=glob_filter).set(total_files)
                self.errors.labels(source="fetch_emulator").set(0)
        except Exception as ex:
            self.log.error(f"{self._module}.{self._class}.{_method}", str(ex), traceback.format_exc())
            self.errors.labels(source="fetch_emulator").set(1)

    def fetch(self):
        """Fetch metrics from the database"""
        _method = inspect.stack()[1][3]
        for path in self.config.paths:
            for emulator in self.config.emulators:
                self._fetch_emulator(path, emulator)
