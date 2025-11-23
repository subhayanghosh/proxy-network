output "proxy_endpoints" {
  description = "List of proxy endpoints in format http://user:pass@ip:3128"
  value = [
    for ip in module.proxy_cluster.proxy_ips :
    "http://${var.proxy_username}:${var.proxy_password}@${ip}:3128"
  ]
  sensitive = true
}
