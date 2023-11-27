import time
from pyspark.sql import SparkSession, functions as F
from pyspark import SparkContext
"""
Create a bucket named datasets on MinIO UI

Upload iris.csv to MinIO

connect spark-client container
docker exec -it spark-client bash

spark-submit --master spark://spark-master:7077 /opt/examples/simple_submit.py
"""
accessKeyId='spark'
secretAccessKey='Ankara06'

# create a SparkSession
spark = SparkSession.builder.appName("Spark Example MinIO").getOrCreate()


def load_config(spark_context: SparkContext):
    spark_context._jsc.hadoopConfiguration().set('fs.s3a.access.key', accessKeyId)
    spark_context._jsc.hadoopConfiguration().set('fs.s3a.secret.key', secretAccessKey)
    spark_context._jsc.hadoopConfiguration().set('fs.s3a.path.style.access', 'true')
    spark_context._jsc.hadoopConfiguration().set('fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem')
    spark_context._jsc.hadoopConfiguration().set('fs.s3a.endpoint', 'http://minio:9000')

load_config(spark.sparkContext)

df = spark.read.format('csv').option('header','true') \
.load('s3a://datasets/iris.csv')

df.select(df.columns[:5]).show()
time.sleep(30)

spark.stop()
