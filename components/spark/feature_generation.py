from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--input")
parser.add_argument("--output")

args = parser.parse_args()

spark = SparkSession.builder.appName(
    "feature-generation"
).getOrCreate()

df = spark.read.parquet(args.input)

df = df.filter(
    (F.col("revenue") > 0)
    &
    (F.col("impressions") > 0)
)

features = (
    df.groupBy("publisher_id")
    .agg(
        F.sum("impressions").alias(
            "impressions_7d"
        ),
        F.sum("clicks").alias(
            "clicks_7d"
        ),
        F.sum("revenue").alias(
            "revenue_7d"
        )
    )
)

features = (
    features
    .withColumn(
        "ctr_7d",
        F.col("clicks_7d")
        /
        F.col("impressions_7d")
    )
    .withColumn(
        "rpm_7d",
        (
            F.col("revenue_7d")
            * 1000
        )
        /
        F.col("impressions_7d")
    )
)

features.write.mode(
    "overwrite"
).parquet(args.output)