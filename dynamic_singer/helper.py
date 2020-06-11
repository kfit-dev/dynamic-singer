import threading
import json
from datetime import date, datetime
from decimal import Decimal
from dynamic_singer import function
from jsonschema import validate
from genson import SchemaBuilder
from singer.messages import SchemaMessage, RecordMessage, format_message
from prometheus_client import Counter, Summary, Histogram
from herpetologist import check_type
from typing import Callable
import singer
import logging

logger = logging.getLogger(__name__)
type_mapping = {'int': 'integer', 'float': 'number', 'str': 'string'}


class Tap:
    @check_type
    def __init__(self, tap, tap_schema, tap_name: str, tap_key: str):

        if not tap_schema is None and not isinstance(tap_schema, dict):
            raise ValueError('tap_schema must be None or a dict')

        self.tap = tap
        self.tap_schema = tap_schema
        self.tap_name = tap_name
        self.tap_key = tap_key

        if not self.tap_schema:
            self.builder = SchemaBuilder()
            self.builder.add_schema({'type': 'object', 'properties': {}})

    def __iter__(self):
        return self

    def __next__(self):
        row = self.tap.emit()
        if row:
            if not isinstance(row, dict):
                raise ValueError('tap.emit() must returned a dict')
            if self.tap_key not in row:
                raise ValueError('tap key not exist in elements from tap')

            if not self.tap_schema:
                self.builder.add_object(row)
                schema = self.builder.to_schema()
            else:
                schema = self.tap_schema

            if isinstance(self.tap_key, (str, bytes)):
                key_properties = [self.tap_key]
            if not isinstance(key_properties, list):
                raise Exception('tap key must be a string or list of strings')

            r = SchemaMessage(
                stream = self.tap_name,
                schema = schema,
                key_properties = key_properties,
                bookmark_properties = None,
            )
            s = format_message(r)
            r = RecordMessage(
                stream = self.tap_name, record = row, time_extracted = None
            )
            r = format_message(r)
            row = (s.encode(), r.encode())
        return row


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


def transformation(rows, builder, function: Callable, tap_schema = None):

    results = []

    for line in rows:
        try:
            msg = singer.parse_message(line)
        except json.decoder.JSONDecodeError:
            logger.error('Unable to parse:\n{}'.format(line))
            raise

        if isinstance(msg, singer.RecordMessage):
            record = msg.record
            record = function(record)
            if record:
                if isinstance(record, tuple):
                    if len(record) != 2:
                        raise ValueError(
                            'transformation must returned (row, dictionary) or row.'
                        )
                    record, types = record
                else:
                    types = None
                builder.add_object(record)
                schema = builder.to_schema()
                if tap_schema:
                    for k, v in tap_schema['properties'].items():
                        if k in schema['properties']:
                            schema['properties'][k] = v
                if types:
                    for k, v in types.items():
                        if k in schema['properties']:
                            v = type_mapping.get(v, v)
                            if not isinstance(v, str):
                                raise ValueError(
                                    f'value {v} from {k} not supported.'
                                )
                            schema['properties'][k] = {'type': v}

                tap_name = msg.stream
                r = SchemaMessage(
                    stream = tap_name,
                    schema = schema,
                    key_properties = None,
                    bookmark_properties = None,
                )
                s = format_message(r)
                r = RecordMessage(
                    stream = tap_name, record = record, time_extracted = None
                )
                r = format_message(r)
                row = [s.encode(), r.encode()]
                results.extend(row)

        else:
            results.append(line)

    return results


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date) or isinstance(obj, datetime):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
