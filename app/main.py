import asyncio
import os
import signal
from concurrent.futures import ProcessPoolExecutor
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from libs.colors import Colors
from metrics.exporter import MetricsExporter

def sighandler(signum, frame):
    print(Colors.colorize(Colors.FGYELLOW, "<SIGTERM received>"))
    exit(0)


def main():
    try:
        exporter = MetricsExporter()
        exporter.run()
        pass
    except KeyboardInterrupt:
        print(Colors.colorize(Colors.FGYELLOW, "<KeyboardInterrupt received>"))
        exit(0)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    signal.signal(signal.SIGTERM, sighandler)
    try:
        executor = ProcessPoolExecutor(2)
        loop.run_in_executor(executor, main)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
