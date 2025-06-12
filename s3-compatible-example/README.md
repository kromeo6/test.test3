# Kubeflow Pipelines with an **external** S3-compatible object store

This scenario is identical in spirit to the AWS S3 migration, but assumes the object store
is **not** AWS — e.g. a standalone MinIO, Ceph RGW, Wasabi, Digital Ocean Spaces, etc.

The key differences are:
1.  You control the **endpoint URL** (host:port).
2.  TLS support and path-style addressing may vary, so `insecure`, `disableSSL`, and
    `forcePathStyle` flags become important.
3.  "Regions" are usually meaningless; pick any string or omit the field if the backend
    does not care.

Below are working, namespace-agnostic manifests you can copy into a *separate* directory,
apply with `kubectl`, or feed into `kustomize`.

---
## Directory contents
| File | Purpose |
|------|---------|
| `workflow-controller-configmap.yaml` | Points Argo (central log & artifact repo) to the external store |
| `kfp-launcher-configmap.yaml`        | Tells every task pod where to read/write input & output artifacts |
| `create-secret.sh`                   | Helper script to create the access-key secret in both relevant namespaces |

---
## Quick-start
```bash
# 1) adjust the variables below
export ENDPOINT="minio.corp.local:9000"   # DNS or IP + port
export BUCKET="mlpipeline"                # bucket must exist in the store
export ACCESS_KEY="ACCESS123"             # s3-style access key
export SECRET_KEY="SECRETabc"             # s3-style secret key

# 2) create secrets in both namespaces
./create-secret.sh $ACCESS_KEY $SECRET_KEY

# 3) apply configmaps (edit first!)
kubectl apply -f workflow-controller-configmap.yaml
kubectl apply -f kfp-launcher-configmap.yaml

# 4) restart long-running deployments
kubectl -n kubeflow rollout restart deployment workflow-controller ml-pipeline

# 5) submit a test pipeline run
```

> **Tip**   For self-hosted MinIO without TLS use `endpoint: "minio.corp.local:9000"` 
> and set `insecure: true` (workflow-controller) **and** `disableSSL: true` (launcher).

---
### What changed compared to the AWS recipe?
| Item | AWS S3 | External store |
|------|--------|----------------|
| `endpoint`          | `s3.${REGION}.amazonaws.com` | host + port you provide |
| `region`            | real AWS region              | any placeholder or omit |
| `insecure / disableSSL` | `false`                   | `true` if no TLS |
| `forcePathStyle`    | usually `true`               | **must** be `true` for MinIO |
| `signatureVersion`  | (omit)                       | (omit) – most KFP/Argo versions don't parse it |

---
## Rollback
Re-apply the original MinIO ConfigMaps or AWS settings and roll-restart the same deployments. 