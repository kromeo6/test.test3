###########################################
##### null for crd, resource for else #####
###########################################

# build crd
# data "external" "build_cert_manager_crd" {
#   # program = ["bash", "-c", "kustomize build nams | jq -sR '{manifest: .}'"]
#   program = ["bash", "-c", "kustomize build manifests/common/cert-manager/base | jq -sR '{manifest: .}'"]
# }

# resource "kubectl_manifest" "inssstal_cert_manager_crd" {
#   depends_on = [data.external.build_cert_manager_crd]

#   for_each = { for idx, obj in split("---", data.external.build_cert_manager_crd.result.manifest) : idx => obj }

#   yaml_body = each.value
# }



resource "null_resource" "cert_manager_crds" {
  provisioner "local-exec" {
    command = <<EOT
      kustomize build manifests/common/cert-manager/base | kubectl apply -f -;
    EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -k manifests/common/cert-manager/base"
  }

  # triggers = {
  #   always_run = timestamp()
  # }
}

# # wait for ready
resource "null_resource" "wait_for_cert_manager" {
  depends_on = [null_resource.cert_manager_crds]

  provisioner "local-exec" {
    command = <<EOT
      echo "Waiting for Cert-Manager to be ready..."
      kubectl wait --for=condition=ready pod -l 'app in (cert-manager,webhook)' --timeout=100s -n cert-manager &&
      kubectl wait --for=jsonpath='{.subsets[0].addresses[0].targetRef.kind}'=Pod endpoints -l 'app in (cert-manager,webhook)' --timeout=100s -n cert-manager
      echo "Waiting additional 20 seconds..."
      sleep 50
    EOT
  }
}

# # issuer from overlay
data "external" "build_certs-issuer-manifests" {
  # depends_on = [null_resource.wait_for_cert_manager] # no dependency here because it wont run during plan
  # program = ["bash", "-c", "kustomize build manifests/common/cert-manager/kubeflow-issuer/base | jq -sR '{manifest: .}'"]
  program = ["bash", "-c", <<EOT
    kustomize build manifests/common/cert-manager/kubeflow-issuer/base | tee ${path.module}/junk/cert-manager-issuer.yaml | jq -sR '{manifest: .}'
  EOT
  ]
}

# before apply the file must be there, otherwise it will return empty and next resource will create null
data "kubectl_path_documents" "read_cert_manager_crds" {
  depends_on = [data.external.build_certs-issuer-manifests]
  pattern    = "${path.module}/junk/cert-manager-issuer.yaml"
}

resource "kubectl_manifest" "inssstal_cert_manager_crd" {
  depends_on = [null_resource.wait_for_cert_manager, data.kubectl_path_documents.read_cert_manager_crds]

  # for_each = { for idx, obj in split("---", data.external.build_certs-issuer-manifests.result.manifest) : idx => obj }
  for_each = toset(data.kubectl_path_documents.read_cert_manager_crds.documents)

  yaml_body = each.value
}







































# # wait for ready
# resource "null_resource" "wait_for_cert_manager" {
#   depends_on = [kubectl_manifest.inssstal_cert_manager_crd]

#   provisioner "local-exec" {
#     command = <<EOT
#       echo "Waiting for Cert-Manager to be ready..."
#       kubectl wait --for=condition=ready pod -l 'app in (cert-manager,webhook)' --timeout=100s -n cert-manager &&
#       kubectl wait --for=jsonpath='{.subsets[0].addresses[0].targetRef.kind}'=Pod endpoints -l 'app in (cert-manager,webhook)' --timeout=100s -n cert-manager
#     EOT
#   }
# }

# # # issuer from overlay
# data "external" "build_certs-issuer-manifests" {
#   # program = ["bash", "-c", "kustomize build nams | jq -sR '{manifest: .}'"]
#   program = ["bash", "-c", "kustomize build manifests/common/cert-manager/kubeflow-issuer/base | jq -sR '{manifest: .}'"]
# }

# # output "test1" {
# #   value = data.external.build_certs-issuer-manifests.result.manifest
# # }


# resource "kubectl_manifest" "cert_issuer" {
#   depends_on = [data.external.build_certs-issuer-manifests, null_resource.wait_for_cert_manager]

#   for_each = { for idx, obj in split("---", data.external.build_certs-issuer-manifests.result.manifest) : idx => obj }

#   yaml_body = each.value
# }



# aqamde





















# data "external" "kustomized_yamlk" {
#   program = [
#     "sh", "-c",
#     "kustomize build overlays/cert-manager | jq -sR '{manifest: .}'"
#   ]
# }

# output "test" {
#   value = data.external.kustomized_yamlk.result.manifest
# }

# resource "kubectl_manifest" "cert_manager" {
#   yaml_body = base64decode(data.external.kustomized_yaml.result["output"])
# }

# resource "kubernetes_manifest" "cert-issuer" {
#   depends_on = [data.external.kustomized_yaml] 
#   for_each = { for idx, obj in split("---", data.external.kustomized_yaml.result.manifest) : idx => obj }

#   manifest = yamldecode(each.value)
# }












# data "kustomization_overlay" "test" {
#   resources = [
#     "overlays/cert-manager",
#   ]
#   kustomize_options {
#     load_restrictor = "none"
#   }
# }


# # first loop through resources in ids_prio[0]
# resource "kustomization_resource" "p0" {
#   for_each = data.kustomization_overlay.test.ids_prio[0]

#   manifest = (
#     contains(["_/Secret"], regex("(?P<group_kind>.*/.*)/.*/.*", each.value)["group_kind"])
#     ? sensitive(data.kustomization_overlay.test.manifests[each.value])
#     : data.kustomization_overlay.test.manifests[each.value]
#   )
# }

# # then loop through resources in ids_prio[1]
# # and set an explicit depends_on on kustomization_resource.p0
# # wait 2 minutes for any deployment or daemonset to become ready
# resource "kustomization_resource" "p1" {
#   for_each = data.kustomization_overlay.test.ids_prio[1]

#   manifest = (
#     contains(["_/Secret"], regex("(?P<group_kind>.*/.*)/.*/.*", each.value)["group_kind"])
#     ? sensitive(data.kustomization_overlay.test.manifests[each.value])
#     : data.kustomization_overlay.test.manifests[each.value]
#   )
#   timeouts {
#     create = "2m"
#   }

#   depends_on = [kustomization_resource.p0]
# }

# # finally, loop through resources in ids_prio[2]
# # and set an explicit depends_on on kustomization_resource.p1
# resource "kustomization_resource" "p2" {
#   for_each = data.kustomization_overlay.test.ids_prio[2]

#   manifest = (
#     contains(["_/Secret"], regex("(?P<group_kind>.*/.*)/.*/.*", each.value)["group_kind"])
#     ? sensitive(data.kustomization_overlay.test.manifests[each.value])
#     : data.kustomization_overlay.test.manifests[each.value]
#   )

#   depends_on = [kustomization_resource.p1]
# }

