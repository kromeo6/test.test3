data "http" "feast_operator_install" {
  url = "https://raw.githubusercontent.com/feast-dev/feast/refs/heads/stable/infra/feast-operator/dist/install.yaml"
}

resource "kubectl_manifest" "feast_crds" {
  for_each = {
    for idx, doc in split("---", data.http.feast_operator_install.response_body) :
    idx => trim(doc)
    if length(trim(doc)) > 0
  }

  yaml_body = each.value
}
