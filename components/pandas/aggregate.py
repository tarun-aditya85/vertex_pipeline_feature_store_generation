from kfp.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=["pandas","pyarrow"]
)
def aggregate_op(
        dataset:Input[Dataset],
        aggregated_dataset:Output[Dataset]
):

    import pandas as pd

    df = pd.read_parquet(dataset.path)

    result = (
        df.groupby("publisher_id")
        .agg(
            impressions_7d=("impressions","sum"),
            clicks_7d=("clicks","sum"),
            revenue_7d=("revenue","sum")
        )
        .reset_index()
    )

    result.to_parquet(aggregated_dataset.path)