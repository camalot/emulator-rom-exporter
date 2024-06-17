import inspect
import os
import traceback
from prometheus_client import start_http_server, Gauge, Enum
from libs.logger import Log
from libs.enums.loglevel import LogLevel
from metrics.emulator import EmulatorRomMetrics
from metrics.config import EmulatorRomMetricsConfig


class MetricsExporter():
    def __init__(self):
        _method = inspect.stack()[0][3]
        self._class = self.__class__.__name__
        self._module = os.path.basename(__file__)[:-3]
        self.config = EmulatorRomMetricsConfig(os.environ.get("ERE_CONFIG_PATH", "/config/config.yml"))

        log_level = LogLevel[self.config.log_level.upper()]
        if not log_level:
            log_level = LogLevel.DEBUG
        self.log = Log(log_level)

        self.log.debug(f"{self._module}.{self._class}.{_method}", f"Exporter initialized")
    def run(self):
        _method = inspect.stack()[1][3]
        try:
            app_metrics = EmulatorRomMetrics(self.config)
            start_http_server(self.config.metrics["port"])
            self.log.info(
                f"{self._module}.{self._class}.{_method}",
                f"Exporter Starting Listen => :{self.config.metrics['port']}/metrics",
            )
            app_metrics.run_metrics_loop()
        except Exception as ex:
            self.log.error(f"{self._module}.{self._class}.{_method}", str(ex), traceback.format_exc())
