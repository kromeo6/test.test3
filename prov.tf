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
    kustomization = {
      source  = "kbst/kustomization"
      version = "0.9.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.10.0"  
    }
  }
}

provider "kubectl" {
  config_path = "/tmp/kubeflow-config"
}

provider "kubernetes" {
  config_path = "/tmp/kubeflow-config"
}

provider "kustomization" {
  kubeconfig_path = "/tmp/kubeflow-config"
}

provider "helm" {
  kubernetes {
    config_path = "/tmp/kubeflow-config"
  }
}