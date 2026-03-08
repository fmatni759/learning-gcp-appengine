# Gestion des Secrets — Guide complet

## Règle absolue
> Aucun secret dans le code. Aucun secret dans Git. Jamais.

---

## Secret Manager GCP — Commandes

```bash
# Activer l'API
gcloud services enable secretmanager.googleapis.com --project=TON_PROJECT_ID

# Créer un secret
gcloud secrets create NOM_SECRET \
  --project=TON_PROJECT_ID \
  --replication-policy="automatic"

# Ajouter une valeur
echo -n "ma-valeur-secrete" | \
  gcloud secrets versions add NOM_SECRET \
  --data-file=- \
  --project=TON_PROJECT_ID

# Lire un secret (pour vérifier)
gcloud secrets versions access latest \
  --secret=NOM_SECRET \
  --project=TON_PROJECT_ID

# Donner accès à un Service Account
gcloud secrets add-iam-policy-binding NOM_SECRET \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=TON_PROJECT_ID
```

---

## Dans le code Python

```python
from google.cloud import secretmanager
import os

def get_secret(secret_id: str) -> str:
    project_id = os.environ.get("PROJECT_ID")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Utilisation
db_password = get_secret("db-password")
api_key = get_secret("external-api-key")
```

```
requirements.txt :
google-cloud-secret-manager==2.16.0
```

---

## GitHub Secrets — Nomenclature standard

| Nom Secret | Contenu | Environnement |
|-----------|---------|---------------|
| `GCP_PROJECT_ID_DEV` | ID projet dev | DEV |
| `GCP_PROJECT_ID_STAGING` | ID projet staging | STAGING |
| `GCP_PROJECT_ID_PROD` | ID projet prod | PROD |
| `WIF_PROVIDER_DEV` | WIF provider dev | DEV |
| `WIF_PROVIDER_STAGING` | WIF provider staging | STAGING |
| `WIF_PROVIDER_PROD` | WIF provider prod | PROD |
| `WIF_SA_DEV` | Service Account dev | DEV |
| `WIF_SA_STAGING` | Service Account staging | STAGING |
| `WIF_SA_PROD` | Service Account prod | PROD |

---

## Ce qui va dans GitHub Secrets vs Secret Manager

| Type | Où mettre |
|------|----------|
| Credentials GCP (WIF) | GitHub Secrets |
| Project IDs | GitHub Secrets |
| Mots de passe DB | Secret Manager GCP |
| Clés API externes | Secret Manager GCP |
| Tokens d'accès | Secret Manager GCP |
| Certificats SSL | Secret Manager GCP |
