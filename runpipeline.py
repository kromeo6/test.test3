import argparse
import json
import yaml
import os
import sys
from client import KFPClientManager
from kfp import compiler, dsl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingest.load import load_dataset


def parse_args():
    parser = argparse.ArgumentParser("Deploy Training Pipeline")
    parser.add_argument("--experiment_name", type=str, help="Experiment Name")
    parser.add_argument("--compute_name", type=str, help="Compute Cluster Name")
    parser.add_argument("--data_name", type=str, help="Data Asset Name")
    parser.add_argument("--environment_name", type=str, help="Registered Environment Name")

    args = parser.parse_args()
    return parser.parse_args()


def main():
    args = parse_args()
    
    try:
        kfp_client = KFPClientManager(
            api_url="http://172.18.255.1/pipeline",
            # api_url="http://localhost:8080/pipeline",
            skip_tls_verify=True,
            dex_username="user@example.com",
            dex_password="12341234",
            # can be 'ldap' or 'local' depending on your Dex configuration
            dex_auth_type="local",
            # cookies="your_session_cookie"
        )
    except Exception as ex:
        print("HERE IN THE EXCEPTION BLOCK")
        print(ex)

    @dsl.pipeline(name='My-Pipeline', description='My test pipeline')
    def test_pipeline():
        load_task = load_dataset()

    compiler.Compiler().compile(test_pipeline, 'test-pipeline.yaml')
    
    # get a newly authenticated KFP client
    # TIP: long-lived sessions might need to get a new client when their session expires
    kfp_client = kfp_client.create_kfp_client()

    run = kfp_client.create_run_from_pipeline_package(
    'test-pipeline.yaml',
    # cookies="your_session_cookie",
    # arguments={
    #     'recipient': 'World',
    # },
    namespace="kubeflow-user-example-com")


if __name__ == "__main__":
    main()
