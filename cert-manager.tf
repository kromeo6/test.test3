# ok versoinkkk
# Cert-Manager CRDs and deployment
resource "kubectl_manifest" "cert_manager" {
  yaml_body = <<YAML
    ${data.external.kustomize_cert_manager.result.manifest}
  YAML

  depends_on = [data.external.kustomize_cert_manager]
}

# External data source to run kustomize
data "external" "kustomize_cert_manager" {
  program = ["bash", "-c", "kustomize build common/cert-manager/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
}

# Wait for cert-manager pods
resource "kubernetes_job" "wait_cert_manager" {
  metadata {
    name      = "wait-cert-manager"
    namespace = "default"
  }

  spec {
    template {
      metadata {}
      spec {
        container {
          name    = "kubectl"
          image   = "bitnami/kubectl"
          command = ["/bin/sh", "-c"]
          args = [<<-EOT
            kubectl wait --for=condition=ready pod -l 'app in (cert-manager,webhook)' --timeout=180s -n cert-manager &&
            kubectl wait --for=jsonpath='{.subsets[0].addresses[0].targetRef.kind}'=Pod endpoints -l 'app in (cert-manager,webhook)' --timeout=180s -n cert-manager
          EOT
          ]
        }
        restart_policy = "Never"
      }
    }
    backoff_limit = 4
  }

  depends_on = [kubectl_manifest.cert_manager]
}

# Cert-Manager Issuer
resource "kubectl_manifest" "cert_manager_issuer" {
  yaml_body = <<YAML
    ${data.external.kustomize_cert_manager_issuer.result.manifest}
  YAML

  depends_on = [kubernetes_job.wait_cert_manager]
}

data "external" "kustomize_cert_manager_issuer" {
  program = ["bash", "-c", "kustomize build common/cert-manager/kubeflow-issuer/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
}

# # Istio CRDs
# resource "kubectl_manifest" "istio_crds" {
#   yaml_body = <<YAML
#     ${data.external.kustomize_istio_crds.result.manifest}
#   YAML

#   depends_on = [kubectl_manifest.cert_manager_issuer]
# }

# data "external" "kustomize_istio_crds" {
#   program = ["bash", "-c", "kustomize build common/istio-1-24/istio-crds/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
# }

# # Istio Namespace
# resource "kubectl_manifest" "istio_namespace" {
#   yaml_body = <<YAML
#     ${data.external.kustomize_istio_namespace.result.manifest}
#   YAML

#   depends_on = [kubectl_manifest.istio_crds]
# }

# data "external" "kustomize_istio_namespace" {
#   program = ["bash", "-c", "kustomize build common/istio-1-24/istio-namespace/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
# }

# # Istio Installation
# resource "kubectl_manifest" "istio_install" {
#   yaml_body = <<YAML
#     ${data.external.kustomize_istio_install.result.manifest}
#   YAML

#   depends_on = [kubectl_manifest.istio_namespace]
# }

# data "external" "kustomize_istio_install" {
#   program = ["bash", "-c", "kustomize build common/istio-1-24/istio-install/overlays/oauth2-proxy | tee /dev/stderr | jq -R -s '{manifest: .}'"]
# }

# # Wait for Istio pods
# resource "kubernetes_job" "wait_istio" {
#   metadata {
#     name      = "wait-istio"
#     namespace = "default"
#   }

#   spec {
#     template {
#       metadata {}
#       spec {
#         container {
#           name    = "kubectl"
#           image   = "bitnami/kubectl"
#           command = ["/bin/sh", "-c"]
#           args    = ["kubectl wait --for=condition=Ready pods --all -n istio-system --timeout 300s"]
#         }
#         restart_policy = "Never"
#       }
#     }
#     backoff_limit = 4
#   }

#   depends_on = [kubectl_manifest.istio_install]
# }