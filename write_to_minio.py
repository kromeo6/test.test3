import pandas as pd
import numpy as np
import io
import boto3

# ========== Configuration ==========
minio_endpoint = "minio-service.kubeflow:9000"  # or "localhost:9000" if port-forwarded
access_key = "<your-access-key>"
secret_key = "<your-secret-key>"
bucket_name = "mlpipeline"
csv_key = "mock-data/sample_dataset.csv"

# ========== Create Mock Data ==========
df = pd.DataFrame({
    'id': range(1, 11),
    'feature_1': np.random.rand(10),
    'feature_2': np.random.randint(100, 200, size=10),
    'label': np.random.choice(['A', 'B'], size=10)
})

# ========== Serialize DataFrame to CSV in memory ==========
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
csv_buffer.seek(0)

# ========== Create MinIO (S3) client ==========
s3 = boto3.client(
    's3',
    endpoint_url=f"http://{minio_endpoint}",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

# ========== Ensure Bucket Exists ==========
try:
    s3.head_bucket(Bucket=bucket_name)
except s3.exceptions.ClientError:
    print(f"Bucket '{bucket_name}' not found. Creating it...")
    s3.create_bucket(Bucket=bucket_name)

# ========== Upload CSV to MinIO ==========
s3.put_object(Bucket=bucket_name, Key=csv_key, Body=csv_buffer.getvalue())

print(f"✅ CSV uploaded successfully to '{bucket_name}/{csv_key}'")


#### read back
obj = s3.get_object(Bucket=bucket_name, Key=csv_key)
df_loaded = pd.read_csv(io.BytesIO(obj['Body'].read()))
print(df_loaded.head())
