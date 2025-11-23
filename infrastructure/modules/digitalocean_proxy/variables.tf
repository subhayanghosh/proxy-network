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

variable "droplet_size" {
  description = "Droplet size slug"
  type        = string
  default     = "s-1vcpu-1gb"
}

variable "name_prefix" {
  description = "Prefix for droplet names"
  type        = string
  default     = "proxy"
}

variable "proxy_username" {
  description = "Username for proxy authentication"
  type        = string
}

variable "proxy_password" {
  description = "Password for proxy authentication"
  type        = string
  sensitive   = true
}
