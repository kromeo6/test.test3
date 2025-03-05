resource "null_resource" "istio_crds" {
  provisioner "local-exec" {
    command = <<EOT
      kustomize build manifests/common/istio-1-24/istio-crds/base | kubectl apply -f -
      kustomize build manifests/common/istio-1-24/istio-namespace/base | kubectl apply -f -
      kustomize build a_overlays/dev/istio/part1 | kubectl apply -f -
    EOT
  }

  provisioner "local-exec" {
    when = destroy
    command = <<EOT
      kubectl delete -k manifests/common/istio-1-24/istio-crds/base
      kubectl delete -k manifests/common/istio-1-24/istio-namespace/base
      kubectl delete -k a_overlays/dev/istio/part1
    EOT
  }
}

# # wait for ready
resource "null_resource" "wait_for_istio_crds" {
  depends_on = [null_resource.istio_crds]

  provisioner "local-exec" {
    command = <<EOT
      echo "Waiting for all Istio Pods to become ready..."
      kubectl wait --for=condition=Ready pods --all -n istio-system --timeout 300s
    EOT
  }
}






# data "external" "build_istio-manifests" {
#   # no dependency here because it wont run during plan
#   program = ["bash", "-c", <<EOT
#     kustomize build manifests/common/istio-1-24/istio-install/overlays/oauth2-proxy | tee ${path.module}/junk/istio-components1.yaml | jq -sR '{manifest: .}'
#   EOT
#   ]
# }

data "external" "build_istio-manifests" {
  # no dependency here because it wont run during plan
  program = ["bash", "-c", <<EOT
    kustomize build a_overlays/dev/istio/part2 | jq -sR '{manifest: .}'
  EOT
  ]
}

# # before apply the file must be there, otherwise it will return empty and next resource will create null
# data "kubectl_path_documents" "read_istio_crds" {
#   depends_on = [data.external.build_istio-manifests]
#   # pattern    = "${path.module}/junk/istio-components.yaml"
#   # pattern    = file("${path.module}/junk/istio-components.yaml")
#   pattern    = replace(file("${path.module}/junk/istio-components.yaml"), "${join("", ["$", "{"])}", "$${")
# }

resource "kubectl_manifest" "inssstal_istio_files" {
  # depends_on = [null_resource.wait_for_cert_manager, data.kubectl_path_documents.read_istio_crds]
  # depends_on = [data.kubectl_path_documents.read_istio_crds]

  for_each = { for idx, obj in split("---", data.external.build_istio-manifests.result.manifest) : idx => obj }
  # for_each = toset(data.kubectl_path_documents.read_istio_crds.documents)

  yaml_body = each.value
}