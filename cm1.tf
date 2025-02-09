# kubernetes.tf

terraform {
  required_providers {
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
    time = {
      source  = "hashicorp/time"
      version = ">= 0.9.0"
    }
  }
}

# Cert-Manager CRDs and deployment
resource "kubectl_manifest" "cert_manager" {
  yaml_body = <<YAML
    ${data.external.kustomize_cert_manager.result.manifest}
  YAML
}

data "external" "kustomize_cert_manager" {
  program = ["bash", "-c", "kustomize build common/cert-manager/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
}

# Wait for initial CRD creation
resource "time_sleep" "wait_for_crds" {
  depends_on = [kubectl_manifest.cert_manager]
  create_duration = "10s"
}

# Check cert-manager and webhook pod readiness
data "kubernetes_resources" "cert_manager_pods" {
  depends_on = [time_sleep.wait_for_crds]

  api_version    = "v1"
  kind           = "Pod"
  label_selector = "app in (cert-manager,webhook)"
  namespace      = "cert-manager"

  timeouts {
    read = "180s"
  }
}

# Check cert-manager and webhook endpoints
data "kubernetes_resources" "cert_manager_endpoints" {
  depends_on = [data.kubernetes_resources.cert_manager_pods]

  api_version    = "v1"
  kind           = "Endpoints"
  label_selector = "app in (cert-manager,webhook)"
  namespace      = "cert-manager"

  timeouts {
    read = "180s"
  }
}

# Additional check to ensure endpoints have addresses
resource "null_resource" "verify_endpoints" {
  depends_on = [data.kubernetes_resources.cert_manager_endpoints]

  triggers = {
    endpoints_check = jsonencode(data.kubernetes_resources.cert_manager_endpoints)
  }

  provisioner "local-exec" {
    command = <<-EOT
      endpoints_json='${jsonencode(data.kubernetes_resources.cert_manager_endpoints.objects)}'
      if ! echo "$endpoints_json" | jq -e 'all(.[] | .subsets[0].addresses[0].targetRef.kind == "Pod")'; then
        echo "Endpoints not ready" >&2
        exit 1
      fi
    EOT
  }
}

# Cert-Manager Issuer
resource "kubectl_manifest" "cert_manager_issuer" {
  yaml_body = <<YAML
    ${data.external.kustomize_cert_manager_issuer.result.manifest}
  YAML

  depends_on = [null_resource.verify_endpoints]
}

data "external" "kustomize_cert_manager_issuer" {
  program = ["bash", "-c", "kustomize build common/cert-manager/kubeflow-issuer/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
}

# Istio CRDs
resource "kubectl_manifest" "istio_crds" {
  yaml_body = <<YAML
    ${data.external.kustomize_istio_crds.result.manifest}
  YAML

  depends_on = [kubectl_manifest.cert_manager_issuer]
  wait = true
}

data "external" "kustomize_istio_crds" {
  program = ["bash", "-c", "kustomize build common/istio-1-24/istio-crds/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
}

# Rest of Istio resources...
# (Istio namespace and installation resources remain the same as in previous example)