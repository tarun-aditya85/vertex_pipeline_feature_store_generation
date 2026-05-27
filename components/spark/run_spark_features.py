from kfp.dsl import component


@component(
    base_image="python:3.11",
    packages_to_install=[
        "google-cloud-dataproc"
    ]
)
def run_spark_features_op(
        project_id:str,
        region:str,
        input_path:str,
        output_path:str):

    from google.cloud import dataproc_v1

    client = (
        dataproc_v1.BatchControllerClient(
            client_options={
                "api_endpoint":
                f"{region}-dataproc.googleapis.com:443"
            }
        )
    )

    batch = {
        "pyspark_batch": {
            "main_python_file_uri":
            "gs://vertex-demo/spark/feature_generation.py",

            "args": [
                "--input",
                input_path,
                "--output",
                output_path
            ]
        }
    }

    operation = client.create_batch(
        request={
            "parent":
            f"projects/{project_id}/locations/{region}",
            "batch": batch,
            "batch_id":
            "feature-job"
        }
    )

    operation.result()