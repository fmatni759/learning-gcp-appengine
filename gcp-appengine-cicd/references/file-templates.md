# 📁 Templates de fichiers — Validés en production

## main.py — Application Flask
```python
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Mon App GCP</title>
    <style>
        body { font-family: Segoe UI, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .card { background: white; border-radius: 20px; padding: 60px; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; }
        h1 { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 Welcome!</h1>
        <p>App Engine + CI/CD Pipeline</p>
    </div>
</body>
</html>'''

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
```

---

## app.yaml — ⚠️ max_instances OBLIGATOIRE depuis mars 2025
```yaml
runtime: python312
env: standard
instance_class: F1

automatic_scaling:
  min_idle_instances: 0
  max_idle_instances: 1
  max_instances: 5

env_variables:
  ENVIRONMENT: "production"

handlers:
  - url: /.*
    script: auto
```

---

## requirements.txt
```
flask==3.0.0
gunicorn==21.2.0
```

---

## .gitignore — ⚠️ key.json TOUJOURS ignoré
```
.terraform/
.terraform.lock.hcl
*.tfstate
*.tfstate.backup
*.tfvars
terraform.tfplan
__pycache__/
*.pyc
.env
venv/
.vscode/
key.json
.DS_Store
```

---

## terraform/providers.tf
```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "TON_PROJECT_ID-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
```

---

## terraform/variables.tf
```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
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
```

---

## terraform/main.tf — ⚠️ PAS de google_app_engine_application !
```hcl
# Activer les APIs necessaires
resource "google_project_service" "appengine" {
  service            = "appengine.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# NOTE IMPORTANT: Ne pas inclure google_app_engine_application ici
# App Engine est cree UNE SEULE FOIS manuellement via le portail GCP
```

---

## terraform/outputs.tf
```hcl
output "app_url" {
  description = "URL de l'application"
  value       = "https://${var.project_id}.nn.r.appspot.com"
}
```

---

## .github/workflows/terraform-plan.yml
```yaml
name: "Terraform Plan"

on:
  pull_request:
    branches: [ main ]

jobs:
  terraform-plan:
    name: "Terraform Plan"
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    steps:
      - name: "Checkout"
        uses: actions/checkout@v4
      - name: "Auth GCP"
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      - name: "Setup Terraform"
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.7.0"
      - name: "Terraform Init"
        working-directory: terraform
        run: terraform init
      - name: "Terraform Validate"
        working-directory: terraform
        run: terraform validate
      - name: "Terraform Plan"
        id: plan
        working-directory: terraform
        run: terraform plan -var="project_id=${{ secrets.GCP_PROJECT_ID }}" -var="environment=dev" -no-color
        continue-on-error: true
      - name: "Commenter PR"
        uses: actions/github-script@v7
        with:
          script: |
            const output = `## Terraform Plan\n\`\`\`\n${{ steps.plan.outputs.stdout }}\n\`\`\`\nStatut: ${{ steps.plan.outcome == 'success' && 'Succes' || 'Echec' }}`;
            github.rest.issues.createComment({ issue_number: context.issue.number, owner: context.repo.owner, repo: context.repo.repo, body: output });
      - if: steps.plan.outcome == 'failure'
        run: exit 1
```

---

## .github/workflows/terraform-apply.yml — ⚠️ timeout-minutes: 15 OBLIGATOIRE
```yaml
name: "Deploy - App Engine + Terraform Apply"

on:
  push:
    branches: [ main ]

jobs:
  terraform-apply:
    name: "Terraform Apply"
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - name: "Checkout"
        uses: actions/checkout@v4
      - name: "Auth GCP"
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      - name: "Setup Terraform"
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.7.0"
      - name: "Terraform Init"
        working-directory: terraform
        run: terraform init
      - name: "Terraform Apply"
        working-directory: terraform
        run: terraform apply -var="project_id=${{ secrets.GCP_PROJECT_ID }}" -var="environment=prod" -auto-approve -no-color

  deploy-appengine:
    name: "Deploy App Engine"
    runs-on: ubuntu-latest
    needs: terraform-apply
    timeout-minutes: 15
    permissions:
      contents: read
      id-token: write
    steps:
      - name: "Checkout"
        uses: actions/checkout@v4
      - name: "Auth GCP"
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      - name: "Deploy App Engine"
        uses: google-github-actions/deploy-appengine@v2
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          promote: true
      - name: "URL"
        run: echo "URL https://${{ secrets.GCP_PROJECT_ID }}.nn.r.appspot.com"
```
