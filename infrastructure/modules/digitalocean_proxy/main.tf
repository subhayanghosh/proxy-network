terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

resource "digitalocean_droplet" "proxy_node" {
  count    = var.node_count
  image    = "ubuntu-22-04-x64"
  name     = "${var.name_prefix}-${count.index + 1}"
  region   = var.region
  size     = var.droplet_size
  tags     = ["proxy-node"]
  
  user_data = templatefile("${path.module}/cloud-init.yaml", {
    proxy_username = var.proxy_username
    proxy_password = var.proxy_password
  })
}

resource "digitalocean_firewall" "proxy_firewall" {
  name = "${var.name_prefix}-firewall"

  droplet_ids = digitalocean_droplet.proxy_node.*.id

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "3128"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
