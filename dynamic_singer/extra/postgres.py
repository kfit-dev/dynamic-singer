import pandas as pd
from dynamic_singer.helper import Encoder
from psycopg2.extras import RealDictCursor
from herpetologist import check_type
import time
import json
import logging

logger = logging.getLogger(__name__)


@check_type
def bigquery_schema(schema: str, table: str, connection):
    """
    Generate bigquery schema.

    Parameters
    ----------
    schema: str
        postgres schema.
    table: str
        table name.
    connection: object
        psycopg2 connection object.

    Returns
    -------
    result : dict
    """

    sql = f"""
        SELECT
        column_name, data_type, is_nullable, udt_name
        FROM
        information_schema.COLUMNS
        WHERE
        TABLE_NAME = '{table}'
        and table_schema = '{schema}';
    """

    df = pd.read_sql(sql, connection)
    schemas = {
        'integer': 'INTEGER',
        'double': 'NUMBER',
        'timestamp': 'STRING',
        'character': 'STRING',
        'text': 'STRING',
        'DEFINED': 'STRING',
        'boolean': 'BOOLEAN',
        'bigint': 'INTEGER',
        'numeric': 'NUMBER',
        'date': 'STRING',
        'int8': 'INTEGER',
        'name': 'STRING',
    }

    nullable = {'NO': 'REQUIRED', 'YES': 'NULLABLE'}

    def sql_type_to_bq_schema(string):
        for k, v in schemas.items():
            if k in string:
                return v

    schema = {
        '$schema': 'http://json-schema.org/schema#',
        'type': 'object',
        'properties': {},
    }
    for i in range(len(df)):
        schema['properties'][df['column_name'].iloc[i]] = {
            'type': sql_type_to_bq_schema(df['data_type'].iloc[i]).lower()
        }
    return schema


class Tap:
    @check_type
    def __init__(
        self,
        schema: str,
        table: str,
        primary_key: str,
        connection,
        persistent,
        batch_size: int = 100,
        rest_time: int = 10,
        filter: str = '',
        debug: bool = True,
    ):

        """
        Postgres Tap using query statement. If prefer logical replication, use original Tap-Postgres from SingerIO.

        Parameters
        ----------
        schema: str
            postgres schema.
        table: str
            table name.
        primary_key: str
            column acted as primary key.
        connection: object
            psycopg2 connection object.
        persistent: object
            a python object that must has `pull` and `push` method to persist primary_key state.
        batch_size: int, (default=100)
            size of rows for each pull from postgres.
        rest_time: int, (default=10)
            rest for rest_time seconds after done pulled.
        filter: str, (default='')
            sql where statement for additional filter. Example, 'price > 0 and discount > 10', depends on table definition.
        debug: bool, (default=True)
            if true, will print important information.

        """

        if not hasattr(persistent, 'pull') and not hasattr(persistent, 'push'):
            raise ValueError('persistent must has `pull` and `push` method')

        self.schema = schema
        self.table = table
        self.primary_key = primary_key
        self.persistent = persistent
        self.batch_size = batch_size
        self.rest_time = rest_time
        self.i = 0
        self.index = None
        self.batch = []
        self.cursor = connection.cursor(cursor_factory = RealDictCursor)
        self.first_time = True
        self.filter = filter
        self.debug = debug

    def pull(self):
        if self.index is None:
            try:
                self.index = self.persistent.pull()
            except:
                pass

        if self.index:
            if len(self.filter):
                where = f"where {self.primary_key} > '{self.index}' and {self.filter}"
            else:
                where = f"where {self.primary_key} > '{self.index}'"
        else:
            if len(self.filter):
                where = f'where {self.filter}'
            else:
                where = ''

        query = f'select * from "{self.schema}".{self.table} {where} order by {self.primary_key} limit {self.batch_size}'
        if self.debug:
            logger.info(query)

        self.cursor.execute(query)
        r = self.cursor.fetchall()
        self.batch = json.loads(json.dumps(r, cls = Encoder))
        if len(self.batch):
            self.index = self.batch[-1][self.primary_key]

        if self.debug:
            logger.info(f'current primary key: {self.index}')

        self.persistent.push(self.index)
        self.first_time = False

    def emit(self):
        while self.i == len(self.batch):
            if not self.first_time:
                time.sleep(self.rest_time)
            self.pull()
            self.i = 0

        self.i += 1
        return self.batch[self.i - 1]
