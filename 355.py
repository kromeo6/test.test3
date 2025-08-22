#!/usr/bin/env python3

import pyspark
from pyspark.sql import SparkSession

def test_s3_minio():
    """Test S3/MinIO connectivity with configurable endpoint"""
    
    print("Testing S3/MinIO connectivity with Spark Connect 3.5.5...")
    
    # Create Spark session with Spark Connect
    spark = SparkSession.builder \
        .remote("sc://localhost:15002") \
        .appName("S3MinIOTest") \
        .getOrCreate()
    
    print(f"Spark version: {spark.version}")
    print("Spark session created successfully!")
    
    # Create minimal test data
    print("\n--- Creating test DataFrame ---")
    df = spark.range(5).withColumnRenamed("id", "value")
    df.show()
    
    # S3 path (credentials configured in YAML)
    s3_path = "s3a://test-temp-bkt-01/debug-test/"
    
    print(f"\n--- Testing S3 write to: {s3_path} ---")
    print("Using AWS S3 configuration from YAML (eu-central-1)")
    
    try:
        # Write as Parquet
        df.write.mode("overwrite").parquet(s3_path)
        print("✅ Successfully wrote DataFrame to S3/MinIO!")
        
        # Test reading back
        print("\n--- Testing S3/MinIO read ---")
        read_df = spark.read.parquet(s3_path)
        print("Data read from S3/MinIO:")
        read_df.show()
        
    except Exception as e:
        print(f"❌ Error writing to S3: {e}")
        print("\nPossible solutions:")
        print("1. Make sure bucket 'test-temp-bkt-01' exists in AWS S3")
        print("2. Check AWS credentials in YAML configuration")
        print("3. Verify the bucket is in eu-central-1 region")
        print("4. Check if DynamoDB JAR is needed")
    
    # Clean up
    spark.stop()
    print("\nTest completed!")

if __name__ == "__main__":
    test_s3_minio() 
