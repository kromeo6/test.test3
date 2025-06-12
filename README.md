# Kubeflow Pipelines – Switching from in-cluster MinIO to AWS S3

These notes document the exact steps that were applied on a **kind**-based Kubeflow installation (1.8 manifests) to replace the built-in MinIO deployment with an external AWS S3 bucket that uses long-lived (static) credentials.

The same approach works for any on-prem/self-hosted K8s cluster; only namespaces may differ.

---
## 0.  Prerequisites
1.  An S3 bucket – e.g. `mytestbucket8710` – in `eu-central-1`.
2.  An IAM user / access-key pair that can `ListBucket`, `GetObject`, `PutObject`, `DeleteObject` on that bucket.
3.  Kubeflow already installed and working on **kind**; default namespaces used below:
    * `kubeflow`                    – system components (API-server, Argo, …)
    * `kubeflow-user-example-com`  – the user **Profile** namespace where pipelines run
4.  `export KUBECONFIG=/tmp/kubeflow-config` for every command that follows.

---
## 1.  Store AWS credentials as Kubernetes Secrets
### 1.1  Kubeflow system namespace
```bash
kubectl -n kubeflow create secret generic s3-secret \
  --from-literal=some-key-1=<AWS_ACCESS_KEY_ID> \
  --from-literal=some-key-2=<AWS_SECRET_ACCESS_KEY>
```
### 1.2  Profile (run) namespace
```bash
kubectl -n kubeflow-user-example-com create secret generic s3-secret \
  --from-literal=some-key-1=<AWS_ACCESS_KEY_ID> \
  --from-literal=some-key-2=<AWS_SECRET_ACCESS_KEY>
```
*(`kubectl` automatically base-64 encodes the values.)*

---
## 2.  Point the KFP **API-server** at S3
Edit the `ml-pipeline` Deployment and add these env-vars (patch shown in *kustomize* style):
```yaml
spec:
  template:
    spec:
      containers:
      - name: ml-pipeline-api-server
        env:
        - name: OBJECTSTORECONFIG_HOST
          value: "s3.amazonaws.com"
        - name: OBJECTSTORECONFIG_PORT
          value: "443"
        - name: OBJECTSTORECONFIG_REGION
          value: "eu-central-1"
        - name: OBJECTSTORECONFIG_SECURE
          value: "true"
        - name: OBJECTSTORECONFIG_ACCESSKEY
          valueFrom:
            secretKeyRef:
              name: s3-secret
              key: some-key-1
        - name: OBJECTSTORECONFIG_SECRETACCESSKEY
          valueFrom:
            secretKeyRef:
              name: s3-secret
              key: some-key-2
```
Apply & rollout:
```bash
kubectl -n kubeflow rollout restart deployment ml-pipeline
```

---
## 3.  Tell the **KFP Launcher** (task pods) to use S3
Create / patch `ConfigMap/kfp-launcher` **in every profile namespace**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kfp-launcher
  namespace: kubeflow-user-example-com
data:
  defaultPipelineRoot: "s3://mytestbucket8710"
  providers: |-
    s3:
      default:
        endpoint: s3.amazonaws.com
        disableSSL: false
        region: eu-central-1
        forcePathStyle: true
        credentials:
          fromEnv: false
          secretRef:
            secretName: s3-secret
            accessKeyKey: some-key-1
            secretKeyKey: some-key-2
```
(No restart needed; every new pod mounts the updated CM.)

---
## 4.  Tell **Argo Workflow-Controller** to archive logs/artifacts in S3
Patch `ConfigMap/workflow-controller-configmap` in the *kubeflow* namespace:
```yaml
data:
  artifactRepository: |
    archiveLogs: true
    s3:
      bucket: mytestbucket8710
      endpoint: s3.eu-central-1.amazonaws.com
      region: eu-central-1
      insecure: false
      accessKeySecret:
        name: s3-secret
        key: some-key-1
      secretKeySecret:
        name: s3-secret
        key: some-key-2
```
*(Note: do **not** include `signatureVersion`; that field is unsupported in the Argo version shipped with Kubeflow 1.8.)*

Reload controller:
```bash
kubectl -n kubeflow rollout restart deployment workflow-controller
```

---
## 5.  Confirm a pipeline run works
1.  Submit a new run from the UI or SDK.
2.  In the profile namespace watch the first pod (root-driver):
   ```bash
   NS=kubeflow-user-example-com
   kubectl -n $NS logs -l workflows.argoproj.io/workflow=<RUN_ID> -f
   ```
   Expect lines like `Uploading to s3://mytestbucket8710/...`.
3.  All step pods should go `Completed` and artifacts appear under that S3 path.

---
## 6.  (Optional) Disable / remove MinIO
If everything works and you want to reclaim local resources:
```bash
# stop workload – reversible
kubectl -n kubeflow scale statefulset minio --replicas 0
kubectl -n kubeflow delete service minio-service

# delete secrets & PVC (only if sure!)
kubectl -n kubeflow delete secret mlpipeline-minio-artifact --ignore-not-found
kubectl -n kubeflow delete pvc data-minio-0 --ignore-not-found
```
MinIO can be re-enabled by scaling the StatefulSet back to 1 and recreating the service.

---
## 7.  Troubleshooting tips
| Symptom | Likely cause |
|---------|--------------|
| Pod fails with `references non-existent secret key` | Secret not present in the same namespace or key names mismatch |
| Driver exits `i/o timeout` to `8080` | Istio side-car on `metadata-grpc` server; wait for ready or set PeerAuthentication to `PERMISSIVE` |
| Argo controller crash-loops with `unknown field "signatureVersion"` | Remove that field from `workflow-controller-configmap` |
| Old runs still show MinIO path | Only new runs pick up changes; old logs remain where they were |

---
## 8.  Rollback
Revert patches, recreate MinIO service, and scale the StatefulSet to 1. That's all.

---
### Credits
This README is generated from the real migration steps executed on this repository. 