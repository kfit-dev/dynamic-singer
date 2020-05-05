import threading
from dynamic_singer import function
from jsonschema import validate
from genson import SchemaBuilder
from singer.messages import SchemaMessage, RecordMessage, format_message
from prometheus_client import start_http_server, Counter, Summary, Histogram
from herpetologist import check_type


class Tap:
    @check_type
    def __init__(
        self, source, source_schema, source_name: str, source_key: str
    ):
        self.source = source
        self.source_schema = source_schema
        self.source_name = source_name
        self.source_key = source_key
        self._send_schema = True
        self._temp = None

        if not self.source_schema:
            self.builder = SchemaBuilder()
            self.builder.add_schema({'type': 'object', 'properties': {}})

    def __iter__(self):
        return self

    def __next__(self):
        if self._temp is None:
            row = self.source.emit()
            if not isinstance(row, dict):
                raise ValueError('source.emit() must returned a dict')
            if self.source_key not in row:
                raise ValueError('source key not exist in elements from source')

            if not self.source_schema:
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
                stream = self.source_name,
                schema = schema,
                key_properties = None,
                bookmark_properties = None,
            )
        else:
            self._temp = None
            self._send_schema = True
            r = RecordMessage(
                stream = self.source_name, record = row, time_extracted = None
            )
        return format_message(r)


class Target:
    def __init__(self, target):
        self.target = target
        if isinstance(target, str):
            f = target
        else:
            f = target.__class__.__name__

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
