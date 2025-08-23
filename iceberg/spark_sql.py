from pyspark.sql import SparkSession

def test_iceberg_sql_create():
    print("🧊 Testing Iceberg table creation with SQL...")
    
    try:
        # Connect to Spark Connect
        spark = SparkSession.builder \
            .appName("IcebergSQLCreateTest") \
            .remote("sc://localhost:15002") \
            .getOrCreate()
        
        print("✅ Spark Connect session created successfully!")
        print(f"Spark version: {spark.version}")
        
        # Test 1: Create Iceberg table with SQL DDL
        print("\n📋 Test 1: Creating Iceberg table with SQL...")
        
        # Drop table if exists
        try:
            spark.sql("DROP TABLE IF EXISTS local.default.sql_created_table")
            print("🗑️ Dropped existing table (if any)")
        except Exception as e:
            print(f"Note: Table didn't exist: {e}")
        
        # Create table using SQL
        create_sql = """
        CREATE TABLE local.default.sql_created_table (
            id BIGINT,
            name STRING,
            age INT,
            salary DOUBLE,
            created_at TIMESTAMP
        ) USING ICEBERG
        """
        
        spark.sql(create_sql)
        print("✅ Iceberg table created with SQL!")
        
        # Test 2: Insert data using SQL
        print("\n📊 Test 2: Inserting data with SQL...")
        
        insert_sql = """
        INSERT INTO local.default.sql_created_table VALUES
        (1, 'Alice', 30, 75000.50, current_timestamp()),
        (2, 'Bob', 25, 60000.00, current_timestamp()),
        (3, 'Charlie', 35, 85000.75, current_timestamp())
        """
        
        spark.sql(insert_sql)
        print("✅ Data inserted with SQL!")
        
        # Test 3: Query the table
        print("\n🔍 Test 3: Querying the table...")
        
        result = spark.sql("SELECT * FROM local.default.sql_created_table ORDER BY id")
        result.show()
        
        count = spark.sql("SELECT COUNT(*) as total FROM local.default.sql_created_table").collect()[0]['total']
        print(f"Total rows: {count}")
        
        # Test 4: Show table structure
        print("\n🏗️ Test 4: Table structure...")
        
        spark.sql("DESCRIBE local.default.sql_created_table").show()
        
        # Test 5: Create table from query (CTAS)
        print("\n🔄 Test 5: Create Table As Select (CTAS)...")
        
        spark.sql("DROP TABLE IF EXISTS local.default.ctas_table")
        
        ctas_sql = """
        CREATE TABLE local.default.ctas_table
        USING ICEBERG
        AS SELECT 
            id,
            upper(name) as upper_name,
            age * 12 as age_months,
            salary
        FROM local.default.sql_created_table
        WHERE age > 25
        """
        
        spark.sql(ctas_sql)
        print("✅ CTAS table created!")
        
        spark.sql("SELECT * FROM local.default.ctas_table").show()
        
        # Test 6: Show all tables in the catalog
        print("\n📚 Test 6: Listing all tables...")
        
        spark.sql("SHOW TABLES IN local.default").show()
        
        # Test 7: Table properties and metadata
        print("\n📋 Test 7: Table properties...")
        
        try:
            spark.sql("SHOW TBLPROPERTIES local.default.sql_created_table").show()
        except Exception as e:
            print(f"Note: SHOW TBLPROPERTIES not supported: {e}")
        
        # Test 8: Insert more data and check versioning
        print("\n🔄 Test 8: Adding more data (Iceberg versioning)...")
        
        spark.sql("""
        INSERT INTO local.default.sql_created_table VALUES
        (4, 'Diana', 28, 70000.00, current_timestamp()),
        (5, 'Eve', 32, 90000.00, current_timestamp())
        """)
        
        final_count = spark.sql("SELECT COUNT(*) as total FROM local.default.sql_created_table").collect()[0]['total']
        print(f"Final row count: {final_count}")
        
        print("\n🎉 ALL SQL TESTS PASSED!")
        print("✅ CREATE TABLE: WORKING")
        print("✅ INSERT INTO: WORKING")
        print("✅ SELECT queries: WORKING")
        print("✅ CTAS: WORKING")
        print("✅ Multiple inserts: WORKING")
        
        spark.stop()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_iceberg_sql_create()
    exit(0 if success else 1) 
