# IAM Policies — Par environnement

## Permissions GitHub Actions SA

```bash
# DEV
gcloud projects add-iam-policy-binding TON_PROJECT_ID-dev \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID-dev.iam.gserviceaccount.com" \
  --role="roles/appengine.deployer"

gcloud projects add-iam-policy-binding TON_PROJECT_ID-dev \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID-dev.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding TON_PROJECT_ID-dev \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID-dev.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding TON_PROJECT_ID-dev \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID-dev.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding TON_PROJECT_ID-dev \
  --member="serviceAccount:github-actions-sa@TON_PROJECT_ID-dev.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageAdmin"

# Répéter pour STAGING et PROD avec leurs projets respectifs
```

## Permissions App Engine SA (bucket staging)

```bash
# Obligatoire pour chaque environnement !
gcloud storage buckets add-iam-policy-binding \
  gs://staging.TON_PROJECT_ID.appspot.com \
  --member="serviceAccount:TON_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding TON_PROJECT_ID \
  --member="serviceAccount:TON_PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"
```

## Tableau récapitulatif permissions

| Service Account | Role | Scope |
|----------------|------|-------|
| github-actions-sa | appengine.deployer | Projet |
| github-actions-sa | cloudbuild.builds.editor | Projet |
| github-actions-sa | storage.admin | Projet |
| github-actions-sa | artifactregistry.admin | Projet |
| github-actions-sa | serviceusage.serviceUsageAdmin | Projet |
| github-actions-sa | iam.serviceAccountUser | Projet |
| PROJECT@appspot | storage.admin | Bucket staging seulement |
| PROJECT@appspot | artifactregistry.admin | Projet |
