from pyspark.sql import SparkSession

def test_complete_functionality():
    print("🧪 Testing complete functionality: MinIO + Iceberg...")
    
    try:
        # Connect to Spark Connect
        spark = SparkSession.builder \
            .appName("CompleteFunctionalityTest") \
            .remote("sc://localhost:15002") \
            .getOrCreate()
        
        print("✅ Spark Connect session created successfully!")
        print(f"Spark version: {spark.version}")
        
        # Create test data
        print("\n📊 Creating test data...")
        df = spark.range(5)  # 0, 1, 2, 3, 4
        print("✅ Test DataFrame created")
        df.show()
        
        # Test 1: Regular Parquet to MinIO (original functionality)
        print("\n📦 Test 1: Regular Parquet write/read...")
        parquet_path = "s3a://test-bucket/test-complete/parquet-data/"
        
        df.write.mode("overwrite").parquet(parquet_path)
        print("✅ Parquet write successful!")
        
        read_parquet = spark.read.parquet(parquet_path)
        print("✅ Parquet read successful!")
        read_parquet.show()
        print(f"Parquet row count: {read_parquet.count()}")
        
        # Test 2: Iceberg table (new functionality)
        print("\n🧊 Test 2: Iceberg table write/read...")
        iceberg_table = "local.default.complete_test"
        
        df.write \
            .format("iceberg") \
            .mode("overwrite") \
            .saveAsTable(iceberg_table)
        print("✅ Iceberg write successful!")
        
        read_iceberg = spark.read \
            .format("iceberg") \
            .table(iceberg_table)
        print("✅ Iceberg read successful!")
        read_iceberg.show()
        print(f"Iceberg row count: {read_iceberg.count()}")
        
        # Test 3: Verify data consistency
        print("\n🔍 Test 3: Data consistency check...")
        parquet_count = read_parquet.count()
        iceberg_count = read_iceberg.count()
        
        if parquet_count == iceberg_count:
            print(f"✅ Data consistency verified! Both have {parquet_count} rows")
        else:
            print(f"❌ Data inconsistency! Parquet: {parquet_count}, Iceberg: {iceberg_count}")
            return False
        
        # Test 4: Operations on both formats
        print("\n🧮 Test 4: Operations on both formats...")
        
        # Parquet operations
        parquet_filtered = read_parquet.filter(read_parquet.id > 2)
        parquet_filtered_count = parquet_filtered.count()
        print(f"Parquet filtered (id > 2): {parquet_filtered_count} rows")
        
        # Iceberg operations  
        iceberg_filtered = read_iceberg.filter(read_iceberg.id > 2)
        iceberg_filtered_count = iceberg_filtered.count()
        print(f"Iceberg filtered (id > 2): {iceberg_filtered_count} rows")
        
        if parquet_filtered_count == iceberg_filtered_count:
            print("✅ Both formats handle filtering correctly!")
        else:
            print("❌ Filtering results differ between formats!")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Regular MinIO parquet operations: WORKING")
        print("✅ Iceberg table operations: WORKING") 
        print("✅ Data consistency: VERIFIED")
        print("✅ Both formats coexist: PERFECTLY")
        
        spark.stop()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_functionality()
    exit(0 if success else 1) 