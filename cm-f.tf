# data "external" "kustomize" {
#   program = ["bash", "-c", "kustomize build nams | jq -sR '{manifest: .}'"]
# }

# resource "kubectl_manifest" "cert-manager-resources" {
#   yaml_body = data.external.kustomize.result.manifest
# }

# data "external" "kustomize1" {
#   program = ["bash", "-c", "kustomize build manifests/common/cert-manager/cert-manager/base | jq -sR '{manifest: .}'"]
# }

# resource "kubernetes_manifest" "kustomize_resources1" {
#   for_each = { for idx, obj in split("---", data.external.kustomize1.result.manifest) : idx => obj }

#   manifest = yamldecode(each.value)
# }

###########################################
##### null for crd, resource for else #####
###########################################

# cert manager crd
resource "null_resource" "cert_manager_crds" {
  provisioner "local-exec" {
    command = <<EOT
      kustomize build manifests/common/cert-manager/cert-manager/base | kubectl apply -f -;
    EOT
  }
}

# wait for ready
resource "null_resource" "wait_for_cert_manager" {
  depends_on = [null_resource.cert_manager_crds]

  provisioner "local-exec" {
    command = <<EOT
      echo "Waiting for Cert-Manager to be ready..."
      kubectl wait --for=condition=ready pod -l 'app in (cert-manager,webhook)' --timeout=100s -n cert-manager &&
      kubectl wait --for=jsonpath='{.subsets[0].addresses[0].targetRef.kind}'=Pod endpoints -l 'app in (cert-manager,webhook)' --timeout=100s -n cert-manager
    EOT
  }
}

# issuer
data "external" "build_certs-issuer-manifests" {
  depends_on = [null_resource.wait_for_cert_manager]  
  program = ["bash", "-c", "kustomize build manifests/common/cert-manager/kubeflow-issuer/base | jq -sR '{manifest: .}'"]
}

resource "kubernetes_manifest" "cert-issuer" {
  depends_on = [data.external.build_certs-issuer-manifests] 
  for_each = { for idx, obj in split("---", data.external.build_certs-issuer-manifests.result.manifest) : idx => obj }

  manifest = yamldecode(each.value)
}


















# output "kustomize_manifest" {
#   value = data.external.kustomize_cert_manager.result
# }

# # Check cert-manager and webhook readiness
# data "kubernetes_resources" "cert_manager_pods" {
#   depends_on = [kubectl_manifest.cert_manager]

#   api_version    = "v1"
#   kind           = "Pod"
#   label_selector = "app in (cert-manager,webhook)"
#   namespace      = "cert-manager"

#   timeouts {
#     read = "180s"
#   }
# }

# # Check endpoints
# data "kubernetes_resources" "cert_manager_endpoints" {
#   depends_on = [data.kubernetes_resources.cert_manager_pods]

#   api_version    = "v1"
#   kind           = "Endpoints"
#   label_selector = "app in (cert-manager,webhook)"
#   namespace      = "cert-manager"

#   timeouts {
#     read = "180s"
#   }
# }

# # Cert-Manager Issuer
# resource "kubectl_manifest" "cert_manager_issuer" {
#   yaml_body = <<YAML
#     ${data.external.kustomize_cert_manager_issuer.result.manifest}
#   YAML

#   depends_on = [data.kubernetes_resources.cert_manager_endpoints]
# }

# data "external" "kustomize_cert_manager_issuer" {
#   program = ["bash", "-c", "kustomize build common/cert-manager/kubeflow-issuer/base | tee /dev/stderr | jq -R -s '{manifest: .}'"]
# }