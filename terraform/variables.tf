variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "learning-gcp-489415"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "northamerica-northeast1"
}

variable "environment" {
  description = "Environment: dev, staging, prod"
  type        = string
  default     = "dev"
}
