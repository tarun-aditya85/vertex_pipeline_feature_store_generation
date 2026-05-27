from kfp import compiler
from kfp.dsl import pipeline

from components.pandas.validate import validate_op
from components.pandas.validate_features import validate_features_op
from components.pandas.write_bq import write_bq_op

from components.spark.run_spark_features import (
    run_spark_features_op
)


@pipeline(
    name="offline-feature-store"
)
def feature_pipeline(
    project_id: str,
    region: str,
    input_path: str,
    feature_output_path: str,
    bq_table: str
):

    validate = validate_op(
        dataset_path=input_path
    )

    spark_job = run_spark_features_op(
        project_id=project_id,
        region=region,
        input_path=input_path,
        output_path=feature_output_path
    )

    validated_features = validate_features_op(
        feature_path=feature_output_path
    )

    write_bq_op(
        feature_path=feature_output_path,
        table_name=bq_table
    )


if __name__ == "__main__":

    compiler.Compiler().compile(
        pipeline_func=feature_pipeline,
        package_path="pipeline_spec.json"
    )