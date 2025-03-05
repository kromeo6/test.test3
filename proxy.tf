# data "external" "build_oauth-proxy-manifests" {
#   # no dependency here because it wont run during plan
#   program = ["bash", "-c", <<EOT
#     kustomize build common/oauth2-proxy/overlays/m2m-dex-and-kind/ | jq -sR '{manifest: .}'
#   EOT
#   ]
# }


# resource "kubectl_manifest" "inssstal_oauthproxy_files" {
#   depends_on = [data.external.build_oauth-proxy-manifests]
#   for_each = { for idx, obj in split("---", data.external.build_oauth-proxy-manifests.result.manifest) : idx => obj }
#   yaml_body = each.value
# }

# resource "null_resource" "wait_for_oauthproxy" {
#   depends_on = [kubectl_manifest.inssstal_oauthproxy_files]

#   provisioner "local-exec" {
#     command = <<EOT
#       echo "Waiting for all oauth proxy Pods to become ready..."
#       kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name=oauth2-proxy' --timeout=180s -n oauth2-proxy
#       kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name=cluster-jwks-proxy' --timeout=180s -n istio-system
#     EOT
#   }
# }