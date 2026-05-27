from kfp.dsl import component, Output, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=["pandas","pyarrow"]
)
def ingest_op(
        input_path:str,
        output_dataset:Output[Dataset]
):

    import pandas as pd

    df = pd.read_parquet(input_path)

    df.to_parquet(output_dataset.path)