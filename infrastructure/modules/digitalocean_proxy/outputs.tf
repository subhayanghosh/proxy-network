output "proxy_ips" {
  description = "List of public IP addresses of the proxy nodes"
  value       = digitalocean_droplet.proxy_node.*.ipv4_address
}
