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

# Wait for cert-manager webhook to be ready
resource "time_sleep" "wait_for_cert_manager" {
  depends_on = [kubectl_manifest.cert_manager]

  create_duration = "30s"
}

# Check cert-manager webhook readiness
data "kubernetes_resource" "cert_manager_webhook" {
  depends_on = [time_sleep.wait_for_cert_manager]

  api_version = "apps/v1"
  kind        = "Deployment"
  metadata {
    name      = "cert-manager-webhook"
    namespace = "cert-manager"
  }

  timeouts {
    read = "180s"
  }
}

# Cert-Manager Issuer (only proceeds when webhook is ready)
resource "kubectl_manifest" "cert_manager_issuer" {
  yaml_body = <<YAML
    ${data.external.kustomize_cert_manager_issuer.result.manifest}
  YAML

  depends_on = [data.kubernetes_resource.cert_manager_webhook]

  wait = true
  wait_for_rollout = true
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

# Istio Namespace
resource "kubectl_manifest" "istio_namespace" {
  yaml_body = <<YAML
    ${data.external.kustomize_istio_namespace.result.manifest}
  YAML

  depends_on = [kubectl_manifest.istio_crds]
  wait = true
}

data "external" "kustomize_istio_namespace" {
  program = ["bash", "-c", "kustomize build common/istio-1-24/istio-namespace/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
}

# Istio Installation
resource "kubectl_manifest" "istio_install" {
  yaml_body = <<YAML
    ${data.external.kustomize_istio_install.result.manifest}
  YAML

  depends_on = [kubectl_manifest.istio_namespace]
  wait = true
  wait_for_rollout = true
}

data "external" "kustomize_istio_install" {
  program = ["bash", "-c", "kustomize build common/istio-1-24/istio-install/overlays/oauth2-proxy | tee /dev/stderr | jq -R -s '{manifest: .}'"]
}