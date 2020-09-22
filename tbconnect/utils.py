import base64
import hashlib
import os

from django.conf import settings
from google.cloud import bigquery
from google.oauth2 import service_account
from iso6709 import Location


bigquery_client = None
if os.path.isfile(settings.TBCONNECT_BQ_KEY_PATH):
    credentials = service_account.Credentials.from_service_account_file(
        settings.TBCONNECT_BQ_KEY_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    bigquery_client = bigquery.Client(
        credentials=credentials, project=credentials.project_id,
    )


def get_latest_bigquery_timestamp(dataset, model, field):
    query = f"SELECT MAX({field}) AS ts FROM {dataset}.{model}"

    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False

    query_job = bigquery_client.query(query, location="EU", job_config=job_config)
    test = list(query_job.result())
    return test[0][0]


def upload_to_bigquery(dataset, table, fields, data):
    schema = []
    for field, data_type in fields.items():
        schema.append(bigquery.SchemaField(field, data_type))

    job_config = bigquery.LoadJobConfig(
        source_format="NEWLINE_DELIMITED_JSON",
        write_disposition="WRITE_APPEND",
        schema=schema,
    )

    job = bigquery_client.load_table_from_json(
        data, f"{dataset}.{table}", job_config=job_config
    )

    job.result()


def get_processed_records(records):
    data = []
    for record in records:
        data.append(record.get_processed_data())
    return data


def hash_string(text):
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode(
        "utf-8"
    )


def extract_lat_long(location):
    try:
        loc = Location(location)
        return float(loc.lat.degrees), float(loc.lng.degrees)
    except TypeError:
        return None, None
