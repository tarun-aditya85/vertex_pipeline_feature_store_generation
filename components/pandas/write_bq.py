from kfp.dsl import component, Input, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=[
        "pandas",
        "pyarrow",
        "google-cloud-bigquery"
    ]
)
def write_bq_op(
        dataset:Input[Dataset],
        table_name:str
):

    import pandas as pd
    from google.cloud import bigquery

    df = pd.read_parquet(dataset.path)

    client = bigquery.Client()

    job = client.load_table_from_dataframe(
        df,
        table_name
    )

    job.result()