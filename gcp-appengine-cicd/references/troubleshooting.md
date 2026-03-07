# 🔧 Troubleshooting — Erreurs réelles et solutions

## 1. gcloud non reconnu dans PowerShell VS Code

**Erreur :**
```
gcloud: The term 'gcloud' is not recognized
```

**Cause :** gcloud installé dans `Program Files (x86)` — pas dans le PATH PowerShell

**Solution :**
```powershell
Add-Content $PROFILE 'function gcloud { & "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" @args }'
. $PROFILE
```

---

## 2. Terraform remote state bucket inexistant

**Erreur :**
```
Error: Failed to get existing workspaces: 
storage: bucket doesn't exist
```

**Solution :**
```bash
gcloud storage buckets create gs://TON_PROJECT_ID-tfstate --location=northamerica-northeast1
```

---

## 3. App Engine déjà créé — Terraform essaie de le recréer

**Erreur :**
```
Error 403: Permission 'appengine.applications.create' denied
```

**Cause :** `google_app_engine_application` dans `main.tf` alors que App Engine existe déjà

**Solution :** Retirer complètement cette ressource de `main.tf` — App Engine se crée UNE SEULE FOIS via le portail

---

## 4. Clé JSON bloquée par la compagnie

**Erreur :**
```
FAILED_PRECONDITION: Key creation is not allowed on this service account
constraints/iam.disableServiceAccountKeyCreation
```

**Solution :** Utiliser Workload Identity Federation (WIF) — voir ÉTAPE 2 du SKILL.md

---

## 5. app.yaml — max_instances manquant

**Erreur :**
```
WARNING: automatic_scaling.max_instances not specified
App Engine sets default to 20 starting March 2025
```

**Solution :** Toujours inclure dans `app.yaml` :
```yaml
automatic_scaling:
  max_instances: 5
```

---

## 6. app.yaml — syntaxe YAML invalide

**Erreur :**
```
ERROR: mapping values are not allowed here
in "app.yaml", line 2, column 8
```

**Cause :** PowerShell `Set-Content` ajoute des caractères parasites

**Solution :** Éditer directement dans VS Code (Ctrl+A → Delete → Coller le contenu)

---

## 7. Fichier workflow YAML en double

**Erreur :**
```
Invalid workflow file
(Line: 73): 'on' is already defined
```

**Cause :** Le fichier contient deux fois le même contenu

**Solution :** Ouvrir dans VS Code → Ctrl+A → Delete → Recoller le contenu correct

---

## 8. Cloud Build — Permission denied sur bucket staging

**Erreur :**
```
service account XXX@appspot.gserviceaccount.com 
does not have access to bucket staging.XXX.appspot.com
```

**Solution :**
```bash
gcloud storage buckets add-iam-policy-binding gs://staging.TON_PROJECT_ID.appspot.com \
  --member="serviceAccount:TON_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/storage.admin"
```

---

## 9. Cloud Build — artifactregistry permission denied

**Erreur :**
```
Permission 'artifactregistry.repositories.downloadArtifacts' denied
on us.gcr.io/TON_PROJECT_ID/app-engine-tmp/...
```

**Solution :**
```bash
gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:TON_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud services enable containerregistry.googleapis.com artifactregistry.googleapis.com
```

---

## 10. GitHub Actions — Deploy App Engine timeout

**Symptôme :** Job s'arrête sur `Waiting for operation [...]` après 30s

**Cause :** Le déploiement App Engine prend 2-3 minutes — timeout par défaut trop court

**Solution :** Ajouter `timeout-minutes: 15` au job deploy :
```yaml
deploy-appengine:
  timeout-minutes: 15
```

---

## 11. git push rejeté — remote ahead

**Erreur :**
```
! [rejected] main -> main (fetch first)
Updates were rejected because the remote contains work
```

**Solution :**
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

---

## 12. VIM s'ouvre pendant git pull

**Symptôme :** Un éditeur bizarre s'ouvre avec `~` partout

**Solution :**
```
1. Appuie Escape
2. Tape :wq
3. Appuie Enter
```

---

## 13. Workload Identity — attribute condition manquante

**Erreur :**
```
The attribute condition must reference one of the provider's claims
```

**Solution :** Ajouter la condition dans le portail GCP :
```
assertion.repository == "TON_USERNAME/TON_REPO"
```
