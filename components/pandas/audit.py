from kfp.dsl import component, Input, Dataset

@component(
    base_image="python:3.11",
    packages_to_install=[
        "pandas",
        "pyarrow"
    ]
)
def audit_op(
        dataset:Input[Dataset]
):

    import pandas as pd

    df = pd.read_parquet(dataset.path)

    print(
        {
            "rows": len(df),
            "columns": len(df.columns)
        }
    )