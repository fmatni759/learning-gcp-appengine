---
name: gcp-security
description: >
  Skill de sécurité GCP — Standards et règles de sécurité obligatoires pour tous les
  déploiements GCP de l'équipe. Utilise ce skill quand on parle de sécurité GCP,
  IAM, permissions, secrets, Workload Identity, Service Accounts, VPC, audit logs,
  Secret Manager, ou quand on configure un nouveau projet GCP. Déclenche aussi pour :
  "configurer la sécurité", "bonnes pratiques IAM", "gérer les secrets", 
  "principle of least privilege", "audit GCP". Ce skill DOIT être consulté avant
  tout déploiement en production.
---

# 🔒 Skill Sécurité GCP — Standards Obligatoires

## Règle d'or
> **Jamais de clé JSON. Jamais de secrets dans le code. Toujours le minimum de permissions.**

---

## 1. Authentification — Workload Identity Federation (OBLIGATOIRE)

❌ **INTERDIT** :
```bash
# Ne jamais créer de clé JSON
gcloud iam service-accounts keys create key.json  # INTERDIT !
```

✅ **OBLIGATOIRE** :
```bash
# Toujours utiliser Workload Identity Federation
# Voir references/wif-setup.md pour la configuration complète
```

---

## 2. Principle of Least Privilege (Permissions minimales)

### Permissions par rôle — App Engine

| Rôle | Permissions |
|------|------------|
| **GitHub Actions SA** | `appengine.deployer`, `cloudbuild.builds.editor`, `storage.admin`, `artifactregistry.admin`, `serviceusage.serviceUsageAdmin` |
| **App Engine SA** | `storage.admin` sur bucket staging seulement |
| **Développeur** | `appengine.appViewer`, `logging.viewer` |
| **DevOps** | `appengine.appAdmin`, `storage.admin` |

### ❌ Ne jamais donner :
- `roles/owner` à un Service Account
- `roles/editor` à un Service Account
- Permissions à `allUsers` sauf si app publique intentionnellement

---

## 3. Gestion des Secrets

### ❌ INTERDIT dans le code :
```python
# Ne jamais faire ça !
DB_PASSWORD = "mon-mot-de-passe"
API_KEY = "abc123"
```

### ✅ OBLIGATOIRE — Secret Manager :
```bash
# Créer un secret
gcloud secrets create db-password \
  --project=TON_PROJECT_ID \
  --replication-policy="automatic"

# Ajouter la valeur
echo -n "mon-mot-de-passe" | gcloud secrets versions add db-password --data-file=-

# Donner accès au SA
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

```python
# Dans le code Python
from google.cloud import secretmanager

def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

### ✅ Secrets GitHub Actions :
- Toujours via `${{ secrets.NOM_SECRET }}`
- Jamais hardcodé dans le YAML
- Documenter dans `references/secrets-list.md`

---

## 4. .gitignore obligatoire

```gitignore
# Secrets — JAMAIS commiter
key.json
*.json.key
.env
.env.*
secrets/
credentials/

# Terraform state local
*.tfstate
*.tfstate.backup
.terraform/
*.tfvars
```

---

## 5. Audit Logging

```bash
# Activer audit logs sur le projet
gcloud projects get-iam-policy TON_PROJECT_ID > policy.yaml
# Ajouter auditConfigs dans policy.yaml
gcloud projects set-iam-policy TON_PROJECT_ID policy.yaml
```

---

## 6. Checklist Sécurité avant déploiement

- [ ] Workload Identity configuré (pas de clé JSON)
- [ ] Service Account avec permissions minimales seulement
- [ ] Aucun secret dans le code ou les fichiers YAML
- [ ] Secrets dans Secret Manager ou GitHub Secrets
- [ ] `.gitignore` inclut `key.json` et `.env`
- [ ] Audit logging activé
- [ ] `key.json` absent du repo GitHub

---

## Références détaillées

📖 `references/wif-setup.md` — Configuration Workload Identity complète
📖 `references/iam-policies.md` — Politiques IAM par environnement
📖 `references/secrets-management.md` — Guide Secret Manager
