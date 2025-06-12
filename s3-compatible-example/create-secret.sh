#!/usr/bin/env bash
# Usage: ./create-secret.sh <ACCESS_KEY> <SECRET_KEY> [kubeflow namespace] [profile namespace]

set -euo pipefail

ACCESS_KEY=${1:-}
SECRET_KEY=${2:-}
SYSTEM_NS=${3:-kubeflow}
PROFILE_NS=${4:-kubeflow-user-example-com}

if [[ -z "$ACCESS_KEY" || -z "$SECRET_KEY" ]]; then
  echo "Usage: $0 <ACCESS_KEY> <SECRET_KEY> [system-ns] [profile-ns]" >&2
  exit 1
fi

echo "Creating secret in $SYSTEM_NS …"
kubectl -n "$SYSTEM_NS" delete secret s3-secret --ignore-not-found
kubectl -n "$SYSTEM_NS" create secret generic s3-secret \
  --from-literal=some-key-1="$ACCESS_KEY" \
  --from-literal=some-key-2="$SECRET_KEY"

echo "Creating secret in $PROFILE_NS …"
kubectl -n "$PROFILE_NS" delete secret s3-secret --ignore-not-found
kubectl -n "$PROFILE_NS" create secret generic s3-secret \
  --from-literal=some-key-1="$ACCESS_KEY" \
  --from-literal=some-key-2="$SECRET_KEY"

echo "Done." 