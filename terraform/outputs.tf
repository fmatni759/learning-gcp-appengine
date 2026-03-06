output "app_url" {
  description = "URL de l'application App Engine"
  value       = "https://${var.project_id}.appspot.com"
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}
