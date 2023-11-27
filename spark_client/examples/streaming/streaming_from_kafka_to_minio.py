from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

# Initialize Spark Session
accessKeyId='dataops'
secretAccessKey='Ankara06'

# create a SparkSession
spark = SparkSession.builder \
.appName("Spark Example MinIO") \
.config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.0,io.delta:delta-core_2.12:2.4.0") \
.config("spark.hadoop.fs.s3a.access.key", accessKeyId) \
.config("spark.hadoop.fs.s3a.secret.key", secretAccessKey) \
.config("spark.hadoop.fs.s3a.path.style.access", True) \
.config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
.config("spark.hadoop.fs.s3a.endpoint", "https://minio-sinem:9001") \
.getOrCreate()



spark.sparkContext.setLogLevel('ERROR')

# Schema definition for the Kafka JSON payload
customerFields = [
    StructField("customerId", StringType()),
    StructField("customerFName", StringType()),
    StructField("customerLName", StringType()),
    StructField("customerEmail", StringType()),
    StructField("customerPassword", StringType()),
    StructField("customerStreet", StringType()),
    StructField("customerCity", StringType()),
    StructField("customerState", StringType()),
    StructField("customerZipcode", StringType())
]

schema = StructType([
    StructField("payload", StructType([
        StructField("before", StructType(customerFields)),
        StructField("after", StructType(customerFields)),
        StructField("ts_ms", StringType()),
        StructField("op", StringType())
    ]))
])

# Read from Kafka
lines = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "dbserver2.public.links") \
    .load()

# Select and cast the value field to string
lines2 = lines.selectExpr("CAST(value AS STRING)")

# Parse the JSON data
parsedData = lines2.select(from_json(col("value"), schema).alias("data"))

# Flatten the data and select fields
flattenedData = parsedData.select(
    col("data.payload.before.*"),
    col("data.payload.after.*"),
    col("data.payload.ts_ms"),
    col("data.payload.op")
)

# Define checkpoint location
checkpoint_dir = "s3a://change-data-capture/checkpoint"


# Define MinIO (S3) output path
minio_output_path = "s3a://change-data-capture/customers-parquet"

# Write the streaming output to MinIO
streamingQuery = flattenedData \
    .writeStream \
    .format("csv") \
    .outputMode("append") \
    .option("path", minio_output_path) \
    .option("checkpointLocation", checkpoint_dir) \
    .start()

# Start streaming
streamingQuery.awaitTermination()
