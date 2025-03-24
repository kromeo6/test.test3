import kfp
from kfp.client import Client

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from client import KFPClientManager


# initialize a KFPClientManager
kfp_client_manager1 = KFPClientManager(
    # api_url="http://localhost:8080/pipeline",
    skip_tls_verify=True,

    dex_username="user@example.com",
    dex_password="12341234",

    # can be 'ldap' or 'local' depending on your Dex configuration
    dex_auth_type="local",
)

# get a newly authenticated KFP client
# TIP: long-lived sessions might need to get a new client when their session expires
kfp_client = kfp_client_manager1.create_kfp_client()

# experiments = kfp_client.list_experiments(namespace="kubeflow-user-example-com")
# print(experiments)

run = kfp_client.create_run_from_pipeline_package(
    'calc-pipeline.yaml',
    arguments = {'a': 7, 'b': 8},
    namespace="kubeflow-user-example-com",
)
