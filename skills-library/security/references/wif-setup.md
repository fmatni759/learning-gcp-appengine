# Workload Identity Federation — Configuration complète

## Commandes dans l'ordre exact (validées en production)

```bash
# 1. Activer les APIs nécessaires
gcloud services enable iamcredentials.googleapis.com sts.googleapis.com --project=TON_PROJECT_ID

# 2. Créer le pool WIF
gcloud iam workload-identity-pools create "github-pool" \
  --project=TON_PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 3. Créer le provider OIDC
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project=TON_PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == 'TON_USERNAME/TON_REPO'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 4. Créer le Service Account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions SA" \
  --project=TON_PROJECT_ID

# 5. Connecter SA au pool WIF
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com \
  --project=TON_PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/TON_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/TON_USERNAME/TON_REPO"
```

## Valeurs pour les secrets GitHub

```
WIF_PROVIDER = projects/TON_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
WIF_SERVICE_ACCOUNT = github-actions-sa@TON_PROJECT_ID.iam.gserviceaccount.com
```

## Dans GitHub Actions

```yaml
permissions:
  id-token: write    # ← OBLIGATOIRE pour WIF
  contents: read

steps:
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
      service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```
