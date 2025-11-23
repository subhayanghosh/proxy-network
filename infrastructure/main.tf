terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

module "proxy_cluster" {
  source = "./modules/digitalocean_proxy"

  node_count     = var.node_count
  region         = var.region
  proxy_username = var.proxy_username
  proxy_password = var.proxy_password
}
