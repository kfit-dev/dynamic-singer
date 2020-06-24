import os


class BQ_GCS:
    def __init__(
        self,
        bq_client,
        bucket,
        project: str,
        schema: str,
        table: str,
        primary_key: str,
        prefix: str = 'singer_record',
    ):

        """
        Persistency layer for BQ combined with GCS.

        Parameters
        ----------
        bq_client: object
            initiated from `from google.cloud import bigquery`.
        bucket: object
            initiated from `from google.cloud import storage`.
        project: str
            project id.
        schema: str
            BQ schema.
        table: str
            table name.
        primary_key: str
            column acted as primary key.
        prefix: str
            prefix path for GCS.
        """

        self.filename = os.path.join(prefix, f'{schema}-{table}')
        self.schema = schema
        self.table = table
        self.primary_key = primary_key
        self.bq_client = bq_client
        self.bucket = bucket

    def pull(self):
        try:
            sql = f"""
            SELECT {self.primary_key} FROM `{self.schema}.{self.table}` order by {self.primary_key} desc LIMIT 1
            """
            query_job = self.bq_client.query(sql)
            key = list(query_job)[0][0]
        except Exception as e:
            print(e)
            blob = self.bucket.get_blob(self.filename)
            key = (blob.download_as_string()).decode('utf-8')
        return key

    def push(self, data):
        blob = self.bucket.blob(self.filename)
        blob.upload_from_string(data)


class GCS:
    def __init__(
        self,
        bucket,
        schema: str,
        table: str,
        primary_key: str,
        prefix: str = 'singer_record',
    ):

        """
        Persistency layer using GCS.

        Parameters
        ----------
        bucket: object
            initiated from `from google.cloud import storage`.
        schema: str
            BQ schema.
        table: str
            table name.
        primary_key: str
            column acted as primary key.
        prefix: str
            prefix path for GCS.
        """

        self.filename = os.path.join(prefix, f'{schema}-{table}')
        self.schema = schema
        self.table = table
        self.primary_key = primary_key
        self.bucket = bucket

    def pull(self):
        blob = self.bucket.get_blob(self.filename)
        key = (blob.download_as_string()).decode('utf-8')
        return key

    def push(self, data):
        blob = self.bucket.blob(self.filename)
        blob.upload_from_string(data)
