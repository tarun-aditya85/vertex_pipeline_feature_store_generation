from kfp.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=["pandas","pyarrow"]
)
def filter_op(
        dataset:Input[Dataset],
        filtered_dataset:Output[Dataset]
):

    import pandas as pd

    df = pd.read_parquet(dataset.path)

    df = df[
        (df["revenue"] > 0) &
        (df["impressions"] > 0)
    ]

    df.to_parquet(filtered_dataset.path)