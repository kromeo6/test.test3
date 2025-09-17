#!/usr/bin/env python3
"""
Final attempt: Use YAML configuration with environment variables for S3 access.
This avoids RepoConfig issues and might work better.
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from feast import FeatureStore, Entity, FeatureView, Field
from feast.types import Float64, Int64, ValueType
from feast.infra.offline_stores.file_source import FileSource

# Set environment variables for S3 access
os.environ.update({
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "AWS_DEFAULT_REGION": "us-east-1",
    "FEAST_S3_ENDPOINT_URL": "http://localhost:9001"
})

def create_feature_store_yaml():
    """Create feature_store.yaml with file offline store"""
    config = '''
project: yaml_s3_test
provider: local

# File offline store
offline_store:
    type: file

# Local stores
online_store:
    type: sqlite
    path: data/online_store.db



from datetime import timedelta
from feast import Entity, FeatureView, Field
from feast.types import Float64, Int64, ValueType
from feast.infra.offline_stores.file_source import FileSource

# Entity
driver = Entity(
    name="driver_id",
    description="Driver identifier",
    value_type=ValueType.INT64
)

# FileSource pointing to MinIO S3
driver_stats_source = FileSource(
    name="driver_stats_source",
    path="s3://test-bucket/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="Driver stats from MinIO S3",
    s3_endpoint_override="http://localhost:9001"
)

# FeatureView
driver_stats_fv = FeatureView(
    name="driver_stats_from_minio",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float64),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    source=driver_stats_source,
    description="Driver statistics from MinIO S3",
)





#!/usr/bin/env python3
"""
Final clean test: Uses static YAML and Python files for configuration
and tests direct S3 access to MinIO with the upgraded Feast library.
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from feast import FeatureStore

# Set environment variables for S3 access
# This is still needed for the S3 FileSource to connect to MinIO
os.environ.update({
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "AWS_DEFAULT_REGION": "us-east-1",
    "FEAST_S3_ENDPOINT_URL": "http://localhost:9001"
})

def test_minio_direct_read():
    """Test YAML-based configuration with direct S3 access."""
    print("🧪 Testing Final Clean Solution: Static Files + Direct S3 Access")
    print("=" * 60)

    try:
        print("1. Initializing FeatureStore from feature_store.yaml...")
        # Feast will automatically discover and use feature_store.yaml in the current directory
        store = FeatureStore(repo_path=".")
        print("✅ FeatureStore initialized")

        print("\n2. Applying feature definitions from features.py...")
        # The FeatureStore object will find and load definitions from the repo
        import features
        store.apply([
            features.driver,
            features.driver_stats_fv
        ])
        print("✅ Feature definitions applied")

        print("\n3. Testing historical feature retrieval...")
        entity_df = pd.DataFrame({
            "driver_id": [1, 2, 3, 4, 5],
            "event_timestamp": [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=5),
            ]
        })

        print("Entity DataFrame:")
        print(entity_df)

        print("\n4. Getting historical features from MinIO S3...")
        feature_vector = store.get_historical_features(
            entity_df=entity_df,
            features=[
                "driver_stats_from_minio:conv_rate",
                "driver_stats_from_minio:avg_daily_trips"
            ]
        )

        historical_df = feature_vector.to_df()
        print("✅ Successfully retrieved historical features!")
        print("\nHistorical features:")
        print(historical_df)

        print("\n5. Testing feature materialization...")
        store.materialize_incremental(end_date=datetime.now())
        print("✅ Features materialized to online store")

        print("\n6. Testing online feature retrieval...")
        online_features = store.get_online_features(
            features=[
                "driver_stats_from_minio:conv_rate",
                "driver_stats_from_minio:avg_daily_trips"
            ],
            entity_rows=[
                {"driver_id": 1},
                {"driver_id": 2},
                {"driver_id": 3}
            ]
        )

        online_df = online_features.to_df()
        print("✅ Successfully retrieved online features!")
        print("\nOnline features:")
        print(online_df)

        print("\n" + "=" * 60)
        print("🎉 SUCCESS: Final Clean Solution Works!")
        print("   - Configuration: Static feature_store.yaml and features.py")
        print("   - S3 access: Direct to MinIO")
        print("   - No sync, no monkey patches, no string-based code.")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minio_direct_read()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 

registry:
    path: data/registry.db

auth:
    type: no_auth

entity_key_serialization_version: 3
'''
    
    with open("feature_store.yaml", "w") as f:
        f.write(config)
    
    print("✅ Created feature_store.yaml")

def create_features_py():
    """Create features.py with S3 FileSource"""
    features_code = '''
from datetime import timedelta
from feast import Entity, FeatureView, Field
from feast.types import Float64, Int64, ValueType
from feast.infra.offline_stores.file_source import FileSource

# Entity
driver = Entity(
    name="driver_id", 
    description="Driver identifier",
    value_type=ValueType.INT64
)

# FileSource pointing to MinIO S3
driver_stats_source = FileSource(
    name="driver_stats_source",
    path="s3://test-bucket/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="Driver stats from MinIO S3",
    s3_endpoint_override="http://localhost:9001"
)

# FeatureView
driver_stats_fv = FeatureView(
    name="driver_stats",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float64),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    source=driver_stats_source,
    description="Driver statistics from MinIO S3",
)
'''
    
    with open("features.py", "w") as f:
        f.write(features_code)
    
    print("✅ Created features.py")

def test_yaml_s3_access():
    """Test YAML-based configuration with S3 access"""
    print("🧪 Testing YAML Configuration + Direct S3 Access")
    print("=" * 50)
    
    try:
        print("1. Creating configuration files...")
        create_feature_store_yaml()
        create_features_py()
        
        print("\n2. Initializing FeatureStore from YAML...")
        store = FeatureStore(repo_path=".")
        print("✅ FeatureStore initialized")
        
        print("\n3. Applying feature definitions...")
        import features
        store.apply([
            features.driver,
            features.driver_stats_fv
        ])
        print("✅ Feature definitions applied")
        
        print("\n4. Testing historical feature retrieval...")
        entity_df = pd.DataFrame({
            "driver_id": [1, 2, 3, 4, 5],
            "event_timestamp": [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=5),
            ]
        })
        
        print("Entity DataFrame:")
        print(entity_df)
        
        print("\n5. Getting historical features from MinIO S3...")
        feature_vector = store.get_historical_features(
            entity_df=entity_df,
            features=[
                "driver_stats:conv_rate",
                "driver_stats:avg_daily_trips"
            ]
        )
        
        historical_df = feature_vector.to_df()
        print("✅ Successfully retrieved historical features!")
        print("\nHistorical features:")
        print(historical_df)
        
        print("\n6. Testing feature materialization...")
        store.materialize_incremental(end_date=datetime.now())
        print("✅ Features materialized to online store")
        
        print("\n7. Testing online feature retrieval...")
        online_features = store.get_online_features(
            features=[
                "driver_stats:conv_rate",
                "driver_stats:avg_daily_trips"
            ],
            entity_rows=[
                {"driver_id": 1},
                {"driver_id": 2},
                {"driver_id": 3}
            ]
        )
        
        online_df = online_features.to_df()
        print("✅ Successfully retrieved online features!")
        print("\nOnline features:")
        print(online_df)
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS: YAML + Direct S3 Access!")
        print("   - Configuration: YAML (not RepoConfig)")
        print("   - S3 access: Direct to MinIO")
        print("   - No sync required: ✅")
        print("   - No monkey patches: ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_yaml_s3_access()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 
