import threading
from dynamic_singer import function
from jsonschema import validate
from genson import SchemaBuilder
from singer.messages import SchemaMessage, RecordMessage, format_message
from prometheus_client import start_http_server, Counter, Summary, Histogram
from herpetologist import check_type
import logging

logger = logging.getLogger(__name__)


class Tap:
    @check_type
    def __init__(self, tap, tap_schema, tap_name: str, tap_key: str):
        self.tap = tap
        self.tap_schema = tap_schema
        self.tap_name = tap_name
        self.tap_key = tap_key
        self._send_schema = True
        self._temp = None

        if not self.tap_schema:
            self.builder = SchemaBuilder()
            self.builder.add_schema({'type': 'object', 'properties': {}})

    def __iter__(self):
        return self

    def __next__(self):
        if self._temp is None:
            row = self.tap.emit()
            if not isinstance(row, dict):
                raise ValueError('tap.emit() must returned a dict')
            if self.tap_key not in row:
                raise ValueError('tap key not exist in elements from tap')

            if not self.tap_schema:
                self.builder.add_object(row)
        else:
            row = self._temp

        if self._send_schema:
            self._send_schema = False
            schema = builder.to_schema()
            if isinstance(key_properties, (str, bytes)):
                key_properties = [key_properties]
            if not isinstance(key_properties, list):
                raise Exception(
                    'key_properties must be a string or list of strings'
                )
            r = SchemaMessage(
                stream = self.tap_name,
                schema = schema,
                key_properties = None,
                bookmark_properties = None,
            )
        else:
            self._temp = None
            self._send_schema = True
            r = RecordMessage(
                stream = self.tap_name, record = row, time_extracted = None
            )
        return format_message(r)


class Target:
    def __init__(self, target, target_str):
        self.target = target
        if isinstance(target_str, str):
            f = target_str
        else:
            f = target_str.__class__.__name__

        f = function.parse_name(f)

        self._tap_count = Counter(f'total_{f}', f'total rows {f}')
        self._tap_data = Summary(
            f'data_size_{f}', f'summary of data size {f} (KB)'
        )
        self._tap_data_histogram = Histogram(
            f'data_size_histogram_{f}', f'histogram of data size {f} (KB)'
        )


class Check_Error(threading.Thread):
    def __init__(self, pipe):
        self.pipe = pipe
        threading.Thread.__init__(self)

    def run(self):
        with self.pipe.stderr:
            function.log_subprocess_output(self.pipe.stderr)


class Check_Pipe(threading.Thread):
    def __init__(self, pipe, debug):
        self.pipe = pipe
        self.debug = debug
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                output = function.non_block_read(self.pipe).strip()
                if output and self.debug:
                    logger.info(output)
        except:
            pass
