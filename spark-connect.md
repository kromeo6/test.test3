# SparkConnect with Kubeflow Notebooks - Complete Setup Guide

This guide documents how to set up and use SparkConnect with Kubeflow notebooks, which provides a simpler alternative to the Enterprise Gateway approach.

## Overview

SparkConnect is a newer feature in Spark 3.4+ that allows clients (like notebooks) to connect to a remote Spark cluster using a lightweight protocol. This approach is much simpler than the Enterprise Gateway setup and doesn't require special kernels.

## Prerequisites

- ✅ Kubeflow installed and running
- ✅ Spark Operator installed and running
- ✅ A Kubeflow notebook server running

## Step 1: Verify SparkConnect is Available

Check if SparkConnect CRD is available in your cluster:

```bash
kubectl get crd | grep sparkconnect
```

You should see:
```
sparkconnects.sparkoperator.k8s.io
```

## Step 2: Create SparkConnect Server

Create a SparkConnect server using the provided example:

```bash
kubectl apply -f examples/sparkconnect/spark-connect.yaml
```

This creates:
- A SparkConnect server pod
- A service to expose the SparkConnect endpoints
- ConfigMaps for configuration

## Step 3: Verify SparkConnect Server is Running

Check the status of the SparkConnect server:

```bash
kubectl get sparkconnect
```

You should see:
```
NAME            AGE   STATUS   PODNAME
spark-connect   7s    Ready    spark-connect-server
```

Check the pods:
```bash
kubectl get pods | grep spark-connect
```

You should see:
```
spark-connect-server      1/1     Running     0          11s
```

Check the service:
```bash
kubectl get svc | grep spark-connect
```

You should see:
```
spark-connect-server      ClusterIP   10.96.123.171   <none>        7078/TCP,7079/TCP,4040/TCP,15002/TCP
```

## Step 4: Create a Kubeflow Notebook

1. Go to Kubeflow Central Dashboard
2. Navigate to "Notebooks"
3. Create a new notebook server
4. Choose any image (e.g., jupyter-scipy)
5. Start the notebook server

## Step 5: Install Required Python Packages

In your notebook, install the required packages for SparkConnect:

```python
# Install all required packages for SparkConnect
!pip install pyspark[connect] grpcio grpcio-status grpcio-tools

# Also install these additional dependencies
!pip install pandas numpy

print("✅ All packages installed!")
```

## Step 6: Connect to SparkConnect from Notebook

Use the regular Python kernel (no special PySpark kernel needed) and run this code:

```python
from pyspark.sql import SparkSession

# Create Spark session using SparkConnect
spark = SparkSession.builder \
    .remote("sc://spark-connect-server.default.svc:15002") \
    .appName("NotebookTest") \
    .getOrCreate()

print(f"✅ SparkConnect session created successfully!")
print(f"Spark version: {spark.version}")

# Test with simple data
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
df = spark.createDataFrame(data, ["name", "age"])
print("Sample data:")
df.show()

# Simple calculation
avg_age = df.agg({"age": "avg"}).collect()[0]["avg(age)"]
print(f"Average age: {avg_age}")

print("✅ SparkConnect is working!")

# Clean up
spark.stop()
```

## Step 7: Advanced Usage Examples

### Example 1: Working with Larger Datasets

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand

spark = SparkSession.builder \
    .remote("sc://spark-connect-server.default.svc:15002") \
    .appName("LargeDatasetTest") \
    .getOrCreate()

# Create a larger dataset
large_df = spark.range(10000).withColumn("random_value", rand())
print(f"Generated {large_df.count()} rows")

# Perform operations
summary = large_df.describe()
summary.show()

spark.stop()
```

### Example 2: Reading and Writing Data

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .remote("sc://spark-connect-server.default.svc:15002") \
    .appName("DataIOTest") \
    .getOrCreate()

# Create sample data
data = [("Alice", 25, "Engineer"), ("Bob", 30, "Manager"), ("Charlie", 35, "Analyst")]
df = spark.createDataFrame(data, ["name", "age", "role"])

# Write to CSV (if you have write permissions)
# df.write.csv("/tmp/sample_data.csv", header=True)

# Show the data
df.show()

spark.stop()
```

## Troubleshooting

### Issue: Package Installation Problems

If you encounter package installation issues:

```python
# Try upgrading pip first
!pip install --upgrade pip

# Install packages one by one
!pip install pyspark[connect]
!pip install grpcio>=1.48.1
!pip install grpcio-status>=1.48.1
!pip install grpcio-tools
```

### Issue: Connection Refused

If you get connection errors:

1. Check if SparkConnect server is running:
   ```bash
   kubectl get sparkconnect
   kubectl get pods | grep spark-connect
   ```

2. Check the service:
   ```bash
   kubectl get svc | grep spark-connect
   ```

3. Verify the URL format: `sc://spark-connect-server.default.svc:15002`

### Issue: Resource Constraints

If you encounter resource issues:

1. Check cluster resources:
   ```bash
   kubectl describe node
   ```

2. Scale down non-essential services if needed
3. Adjust SparkConnect resource requests in the YAML file

## Port Explanation

The SparkConnect service exposes multiple ports:

- **7078/TCP** - Spark Driver RPC port
- **7079/TCP** - Spark Block Manager port  
- **4040/TCP** - Spark Web UI port
- **15002/TCP** - **SparkConnect protocol port** (use this one)

## Advantages of SparkConnect

✅ **Simpler setup** - No Enterprise Gateway needed  
✅ **No special kernel** - Use regular Python kernel  
✅ **No Java in notebook** - Java runs in the SparkConnect server  
✅ **Direct connection** - Connect directly to Spark cluster  
✅ **Modern approach** - Uses Spark 3.4+ features  

## Cleanup

To remove the SparkConnect server:

```bash
kubectl delete sparkconnect spark-connect
```

## Resources

- [SparkConnect Documentation](https://spark.apache.org/docs/latest/spark-connect-overview.html)
- [Spark Operator Documentation](https://www.kubeflow.org/docs/components/spark-operator/)
- [SparkConnect Example](examples/sparkconnect/spark-connect.yaml)

---

**Note**: This approach is much simpler than the Enterprise Gateway method and doesn't require the complex setup described in the Kubeflow documentation. SparkConnect provides a direct, lightweight connection to your Spark cluster. 
