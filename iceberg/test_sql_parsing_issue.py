from pyspark.sql import SparkSession

def test_basic_sql():
    print("Testing basic SQL functionality...")
    
    try:
        # Connect to Spark Connect
        spark = SparkSession.builder \
            .appName("BasicSQLTest") \
            .remote("sc://localhost:15002") \
            .getOrCreate()
        
        print("✅ Spark Connect session created successfully!")
        print(f"Spark version: {spark.version}")
        
        # Test simple range
        print("\n📊 Testing spark.range...")
        df = spark.range(3)
        df.show()
        
        # Test simple SQL
        print("\n🔍 Testing simple SQL...")
        result = spark.sql("SELECT 1 as test_col")
        result.show()
        
        # Test show databases 
        print("\n🏛️ Testing SHOW DATABASES...")
        try:
            databases = spark.sql("SHOW DATABASES")
            databases.show()
        except Exception as e:
            print(f"⚠️ SHOW DATABASES failed: {e}")
        
        # Test show tables
        print("\n📋 Testing SHOW TABLES...")
        try:
            tables = spark.sql("SHOW TABLES")
            tables.show()
        except Exception as e:
            print(f"⚠️ SHOW TABLES failed: {e}")
        
        # Check Spark configurations
        print("\n⚙️ Checking key Spark configurations...")
        try:
            catalogs_conf = spark.conf.get("spark.sql.catalog.iceberg")
            print(f"Iceberg catalog config: {catalogs_conf}")
        except Exception as e:
            print(f"⚠️ Iceberg catalog config not found: {e}")
        
        try:
            extensions_conf = spark.conf.get("spark.sql.extensions")
            print(f"SQL extensions config: {extensions_conf}")
        except Exception as e:
            print(f"⚠️ SQL extensions config not found: {e}")
        
        print("\n✅ Basic SQL test completed!")
        spark.stop()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_sql()
    exit(0 if success else 1) 