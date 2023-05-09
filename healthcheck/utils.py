import base64
import hashlib
import os
from functools import lru_cache

from google.cloud import bigquery
from google.oauth2 import service_account
from iso6709 import Location


@lru_cache(maxsize=None)
def get_bigquery_client(key_path):
    if os.path.isfile(key_path):
        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        return bigquery.Client(credentials=credentials, project=credentials.project_id,)


def get_latest_bigquery_timestamp(bigquery_client, dataset, model, field):
    query = f"SELECT MAX({field}) AS ts FROM {dataset}.{model}"

    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False

    query_job = bigquery_client.query(query, location="EU", job_config=job_config)
    test = list(query_job.result())
    return test[0][0]


def upload_to_bigquery(bigquery_client, dataset, table, fields, data):
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


def sync_models_to_bigquery(key_path, dataset, models):
    bigquery_client = get_bigquery_client(key_path)
    if bigquery_client:
        for model, details in models.items():
            field = details["field"]
            latest_timestamp = get_latest_bigquery_timestamp(
                bigquery_client, dataset, model, field
            )

            if latest_timestamp:
                records = details["model"].objects.filter(
                    **{f"{field}__gt": latest_timestamp}
                )
            else:
                records = details["model"].objects.all()

            if "filter" in details:
                records = records.filter(
                    **{details["filter"]["key"]: details["filter"]["value"]}
                )

            if records:
                data = get_processed_records(records)
                upload_to_bigquery(
                    bigquery_client, dataset, model, details["fields"], data
                )


def get_processed_records(records):
    data = []
    for record in records:
        data.append(record.get_processed_data())
    return data


def hash_string(text):
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode(
        "utf-8"
    )


def extract_reduced_accuracy_lat_long(location, resolution=1):
    if location:
        loc = Location(location)
        lat = round(float(loc.lat.decimal), resolution)
        lng = round(float(loc.lng.decimal), resolution)
        return (lat, lng)
    else:
        return (None, None)


def get_contact_msisdn(contact):

    for urn in contact:
        if "whatsapp" in urn:
            return "+" + urn.split(":")[1]
