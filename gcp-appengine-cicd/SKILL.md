---
name: gcp-appengine-cicd
description: >
  Guide complet et battle-tested pour déployer une application sur GCP App Engine
  avec GitHub, Terraform et GitHub Actions CI/CD sur Windows avec VS Code.
  Basé sur une expérience réelle incluant toutes les erreurs courantes et leurs solutions.
  Utilise ce skill quand l'utilisateur mentionne : déploiement GCP, App Engine, 
  Terraform, GitHub Actions, CI/CD pipeline, Workload Identity Federation, 
  remote state GCS, Pull Request workflow, gcloud sur Windows, PATH Windows,
  PowerShell avec gcloud, ou toute combinaison de ces concepts.
  Déclenche aussi pour : "déployer mon app sur GCP", "configurer CI/CD avec GitHub",
  "connecter GitHub à GCP", "terraform plan sur Pull Request".
---

# 🚀 Skill : GCP App Engine CI/CD — Battle-Tested

## Stack utilisée (validée en production)
- **OS** : Windows 11 + PowerShell 7
- **IDE** : VS Code
- **Cloud** : GCP App Engine Standard (Python 3.12)
- **IaC** : Terraform 1.14+ avec remote state GCS
- **CI/CD** : GitHub Actions + Workload Identity Federation
- **Auth** : Workload Identity (PAS de clé JSON — bloqué en entreprise)

---

## ⚠️ ERREURS COURANTES ET SOLUTIONS (apprises par expérience)

Lire `references/troubleshooting.md` pour la liste complète des erreurs rencontrées.

---

## ÉTAPE 0 — Prérequis Windows

### Outils à installer
1. **Git** → https://git-scm.com
2. **VS Code** → https://code.visualstudio.com
3. **gcloud CLI** → https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
4. **Terraform** → https://developer.hashicorp.com/terraform/install (AMD64 .zip)

### ⚠️ Terraform PATH sur Windows
```powershell
# 1. Créer C:\terraform\ et mettre terraform.exe dedans
# 2. Ajouter au PATH via Environment Variables → System → Path → New
# Ou tester immédiatement :
$env:PATH += ";C:\terraform"
terraform --version
```

### ⚠️ gcloud sur Windows — Problème connu
gcloud s'installe dans `C:\Program Files (x86)\Google\Cloud SDK\`
PowerShell ne le reconnaît pas comme commande. Solution permanente :

```powershell
# Créer alias permanent dans le profil PowerShell
New-Item -Path $PROFILE -ItemType File -Force
Add-Content $PROFILE 'function gcloud { & "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" @args }'
. $PROFILE
gcloud --version  # doit fonctionner !
```

### Extensions VS Code essentielles
- `hashicorp.terraform`
- `googlecloudtools.cloudcode`
- `github.vscode-pull-request-github`
- `eamodio.gitlens`

---

## ÉTAPE 1 — Configuration GCP

```bash
# Dans Google Cloud SDK Shell (pas PowerShell !)
gcloud auth login
gcloud config set project TON_PROJECT_ID

# Activer les APIs (faire UNE SEULE FOIS manuellement)
gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com iamcredentials.googleapis.com sts.googleapis.com artifactregistry.googleapis.com containerregistry.googleapis.com --project=TON_PROJECT_ID

# Créer App Engine (UNE SEULE FOIS par projet)
# → Faire via le portail GCP console.cloud.google.com
# → App Engine → Create Application → northamerica-northeast1

# Créer bucket remote state Terraform
gcloud storage buckets create gs://TON_PROJECT_ID-tfstate --location=northamerica-northeast1
```

---

## ÉTAPE 2 — Workload Identity Federation (remplace les clés JSON)

> ⚠️ Les clés JSON sont souvent bloquées en entreprise — utiliser WIF !

```bash
# Dans Google Cloud SDK Shell
# 1. Créer le pool
gcloud iam workload-identity-pools create "github-pool" --project=TON_PROJECT_ID --location="global" --display-name="GitHub Actions Pool"

# 2. Créer le provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project=TON_PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == 'TON_USERNAME/TON_REPO'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Créer le Service Account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions SA" \
  --project=TON_PROJECT_ID

# 4. Donner les permissions au SA
gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/appengine.appAdmin"

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/appengine.deployer"

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageAdmin"

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

# 5. Connecter le SA au pool WIF
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com \
  --project=TON_PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/TON_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/TON_USERNAME/TON_REPO"

# 6. Donner accès au bucket staging App Engine
gcloud storage buckets add-iam-policy-binding gs://staging.TON_PROJECT_ID.appspot.com \
  --member="serviceAccount:TON_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --project=TON_PROJECT_ID

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:TON_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"
```

---

## ÉTAPE 3 — Secrets GitHub à configurer

Dans GitHub → repo → Settings → Secrets → Actions :

| Secret | Valeur |
|--------|--------|
| `GCP_PROJECT_ID` | `ton-project-id` |
| `WIF_PROVIDER` | `projects/TON_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `WIF_SERVICE_ACCOUNT` | `github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com` |

---

## ÉTAPE 4 — Structure des fichiers

📖 Voir `references/file-templates.md` pour tous les fichiers complets.

```
mon-app/
├── main.py                    ← app Flask Python
├── app.yaml                   ← config App Engine (inclure max_instances !)
├── requirements.txt           ← flask + gunicorn
├── .gitignore                 ← inclure key.json et .terraform/
├── terraform/
│   ├── providers.tf           ← backend GCS + provider google
│   ├── variables.tf           ← project_id, region, environment
│   ├── main.tf                ← APIs seulement (PAS google_app_engine_application !)
│   └── outputs.tf
└── .github/workflows/
    ├── terraform-plan.yml     ← sur Pull Request
    └── terraform-apply.yml    ← sur merge main (timeout-minutes: 15 !)
```

---

## ÉTAPE 5 — Workflow Git jour-à-jour

```bash
# 1. Créer une branche
git checkout -b feature/ma-feature

# 2. Coder + sauvegarder (Ctrl+S dans VS Code)

# 3. Commiter
git add .
git commit -m "feat: description du changement"
git push origin feature/ma-feature

# 4. Créer Pull Request sur GitHub
# → GitHub Actions lance terraform plan automatiquement
# → Le plan apparaît en commentaire sur la PR

# 5. Merger la PR
# → GitHub Actions lance terraform apply + gcloud app deploy
# → App live sur https://TON_PROJECT_ID.nn.r.appspot.com
```

---

## Points critiques à ne jamais oublier

1. **Ne jamais commiter `key.json`** — toujours dans `.gitignore`
2. **`google_app_engine_application` dans Terraform** — NE PAS inclure si App Engine déjà créé via portail
3. **`max_instances` dans `app.yaml`** — obligatoire depuis mars 2025
4. **`timeout-minutes: 15`** dans le job deploy GitHub Actions — le déploiement App Engine prend du temps
5. **Remote state bucket** — créer manuellement avant `terraform init`
6. **Permissions App Engine SA** — `artifactregistry.admin` requis pour Cloud Build
