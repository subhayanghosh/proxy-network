variable "do_token" {
  description = "DigitalOcean API Token"
  type        = string
  sensitive   = true
}

variable "node_count" {
  description = "Number of proxy nodes to deploy"
  type        = number
  default     = 1
}

variable "region" {
  description = "DigitalOcean region slug"
  type        = string
  default     = "nyc1"
}

variable "proxy_username" {
  description = "Username for proxy authentication"
  type        = string
  default     = "proxyuser"
}

variable "proxy_password" {
  description = "Password for proxy authentication"
  type        = string
  sensitive   = true
}
