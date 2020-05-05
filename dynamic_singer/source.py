import json
import os
import re
import sys
import singer
from subprocess import Popen, PIPE, STDOUT
from dynamic_singer import helper, function
from typing import Callable, Dict
from herpetologist import check_type
from tornado import gen
from prometheus_client import start_http_server, Counter, Summary, Histogram
import logging

logger = logging.getLogger(__name__)


@gen.coroutine
def _sinking(line, target):
    if isinstance(target.target, Popen):
        target.target.stdin.write('{}'.format(line).encode())
        target.target.stdin.flush()
        r = target.target.stdout.readline()
    else:
        r = target.target.parse(line)

    target._tap_count.inc()
    target._tap_data.observe(sys.getsizeof(line) / 1000)
    target._tap_data_histogram.observe(sys.getsizeof(line) / 1000)
    return r


class Source:
    @check_type
    def __init__(
        self,
        source,
        source_schema: Dict = None,
        source_name: str = None,
        source_key: str = None,
        port: int = 8000,
    ):

        if not isinstance(source, str) and not hasattr(source, 'emit'):
            raise ValueError(
                'source must a string or an object with method `emit`'
            )
        if isinstance(source, Callable):
            self.source = helper.Tap(
                source,
                source_schema = source_schema,
                source_name = source_name,
                source_key = source_key,
            )
            f = source_name
        else:
            self.source = source
            f = source
        self._targets = []
        start_http_server(port)
        f = function.parse_name(f)

        self._tap_count = Counter(f'total_{f}', f'total rows {f}')
        self._tap_data = Summary(
            f'data_size_{f}', f'summary of data size {f} (KB)'
        )
        self._tap_data_histogram = Histogram(
            f'data_size_histogram_{f}', f'histogram of data size {f} (KB)'
        )

    def add(self, target):
        if not isinstance(target, str) and not hasattr(source, 'parse'):
            raise ValueError(
                'target must a string or an object with method `parse`'
            )
        self._targets.append(target)

    @check_type
    def start(self, debug = True, asynchronous: bool = False):

        if not len(self._targets):
            raise Exception(
                'targets are empty, please add a target using `source.add()` first.'
            )
        self._pipes, self._threads = [], []
        for target in self._targets:
            if isinstance(target, str):
                p = Popen(
                    target.split(), stdout = PIPE, stdin = PIPE, stderr = PIPE
                )
                t = helper.Check_Error(p)
                t.start()
                self._threads.append(t)
            else:
                p = target

            self._pipes.append(helper.Target(p))

        if isinstance(self.source, str):
            pse = Popen(
                self.source.split(), stdout = PIPE, stdin = PIPE, stderr = PIPE
            )
            t = helper.Check_Error(pse)
            t.start()
            pse = iter(pse.stdout.readline, b'')
        else:
            pse = self.source

        for line in pse:
            if len(line):
                if debug:
                    logger.warning(line)

                self._tap_count.inc()
                self._tap_data.observe(sys.getsizeof(line) / 1000)
                self._tap_data_histogram.observe(sys.getsizeof(line) / 1000)

                if asynchronous:

                    @gen.coroutine
                    def loop():
                        r = yield [_sinking(line, pipe) for pipe in self._pipes]

                    result = loop()
                    if debug:
                        logger.warning(result.result())

                else:
                    for pipe in self._pipes:
                        result = _sinking(line, pipe)
                        if debug:
                            logger.warning(result.result())
