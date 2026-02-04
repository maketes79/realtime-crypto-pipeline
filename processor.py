import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

# -------------------------------------------------------------------------
# 1. AUTO-DETECT SPARK VERSION
#    This prevents "NoSuchMethodError" by ensuring the Kafka connector
#    matches your installed PySpark version exactly.
# -------------------------------------------------------------------------
import pyspark
spark_version = pyspark.__version__
# Fallback for some dev environments
if 'dev' in spark_version:
    spark_version = '3.5.0' # Assume latest stable if dev version found

print(f"--- Detected PySpark Version: {spark_version} ---")

# Define the packages based on the detected version
# We use the Scala 2.12 build which is the default for standard PySpark
kafka_package = f"org.apache.spark:spark-sql-kafka-0-10_2.12:{spark_version}"
postgres_package = "org.postgresql:postgresql:42.6.0"

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
KAFKA_BOOTSTRAP_SERVERS = 'localhost:29092'
KAFKA_TOPIC_NAME = 'crypto_trades'

JDBC_URL = "jdbc:postgresql://localhost:5432/crypto_db"
JDBC_PROPERTIES = {
    "user": "user",
    "password": "password",
    "driver": "org.postgresql.Driver"
}

def write_to_postgres(df, epoch_id):
    """
    Function to write each micro-batch to Postgres.
    """
    # --- DEBUGGING: COUNT THE ROWS ---
    row_count = df.count()
    print(f"--- Batch {epoch_id} contains {row_count} records ---")
    
    if row_count == 0:
        return  # Don't try to write empty data
    # ---------------------------------

    print(f"Writing {row_count} rows to Postgres...")
    try:
        df.write \
            .jdbc(url=JDBC_URL, table="trades", mode="append", properties=JDBC_PROPERTIES)
    except Exception as e:
        print(f"Error writing batch {epoch_id}: {e}")

if __name__ == "__main__":
    # 2. Initialize Spark with DYNAMIC package versions
    print(f"--- Downloading dependencies: {kafka_package}, {postgres_package} ---")
    
    spark = SparkSession.builder \
        .appName("CryptoStreamProcessor") \
        .config("spark.jars.packages", f"{kafka_package},{postgres_package}") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.extraJavaOptions", "-Duser.timezone=UTC") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    # 3. Define Schema
    schema = StructType([
        StructField("symbol", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("quantity", DoubleType(), True),
        StructField("timestamp", LongType(), True)
    ])

    # 4. Read Stream from Kafka
    print("--- Connecting to Kafka... ---")
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC_NAME) \
        .option("startingOffsets", "earliest") \
        .load()

    # 5. Parse Data
    parsed_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

    # 6. Write Stream
    print("--- Starting Stream Processing... ---")
    query = parsed_df.writeStream \
        .foreachBatch(write_to_postgres) \
        .outputMode("append") \
        .start()

    query.awaitTermination()