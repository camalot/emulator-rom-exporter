import sys
import typing

from libs.colors import Colors
from libs.enums import loglevel


class Log:
    def __init__(self, minimumLogLevel: loglevel.LogLevel = loglevel.LogLevel.DEBUG) -> None:
        self.minimum_log_level = minimumLogLevel
        pass

    def __write(
        self,
        level: loglevel.LogLevel,
        method: str,
        message: str,
        stack: typing.Optional[str] = None,
        file: typing.IO = sys.stdout,
    ) -> None:
        color = Colors.get_color(level)
        m_level = Colors.colorize(color, f"[{level.name}]", bold=True)
        m_method = Colors.colorize(Colors.HEADER, f"[{method}]", bold=False)
        m_message = f"{Colors.colorize(color, message)}"
        str_out = f"{m_level} {m_method} {m_message}"
        print(str_out, file=file)
        if stack:
            print(Colors.colorize(color, stack), file=file)

        # if level >= self.minimum_log_level:
        #     self.logs_db.insert_log(guildId=guildId, level=level, method=method, message=message, stack=stack)

    def debug(self, method: str, message: str, stack: typing.Optional[str] = None) -> None:
        self.__write(
            level=loglevel.LogLevel.DEBUG, method=method, message=message, stack=stack, file=sys.stdout
        )

    def info(self, method: str, message: str, stack: typing.Optional[str] = None) -> None:
        self.__write(
            level=loglevel.LogLevel.INFO, method=method, message=message, stack=stack, file=sys.stdout
        )

    def warn(self, method: str, message: str, stack: typing.Optional[str] = None) -> None:
        self.__write(
            level=loglevel.LogLevel.WARNING,
            method=method,
            message=message,
            stack=stack,
            file=sys.stdout,
        )

    def error(self, method: str, message: str, stack: typing.Optional[str] = None) -> None:
        self.__write(
            level=loglevel.LogLevel.ERROR, method=method, message=message, stack=stack, file=sys.stderr
        )

    def fatal(self, method: str, message: str, stack: typing.Optional[str] = None) -> None:
        self.__write(
            level=loglevel.LogLevel.FATAL, method=method, message=message, stack=stack, file=sys.stderr
        )
