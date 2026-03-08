---
name: gcp-env-prod
description: >
  Skill configuration environnement PRODUCTION pour GCP App Engine.
  Utilise ce skill quand on configure ou déploie en production, quand on parle
  de config prod, de release, de go-live, ou de déploiement final.
  Toujours combiner avec gcp-security. Approbation manuelle OBLIGATOIRE.
---

# 🚀 Environnement PROD — Configuration GCP

## ⚠️ Références obligatoires avant déploiement
→ `skills-library/security/SKILL.md` — Sécurité
→ `skills-library/environments/dev/SKILL.md` — Valider en DEV d'abord !

---

## Caractéristiques PROD

| Paramètre | Valeur PROD | Raison |
|-----------|------------|--------|
| `max_instances` | 20 | Gérer le trafic réel |
| `instance_class` | F2 | Plus de performance |
| `min_idle_instances` | 1 | Pas de cold start |
| Déploiement | Manuel approuvé | Sécurité maximale |
| Données | Réelles | Protégées par sécurité |
| Logs | INFO seulement | Pas de données sensibles dans logs |

---

## app.yaml — PROD
```yaml
runtime: python312
env: standard
instance_class: F2

automatic_scaling:
  min_idle_instances: 1       # ← toujours une instance active
  max_idle_instances: 3
  max_instances: 20           # ← gérer le vrai trafic

env_variables:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"           # ← pas DEBUG en prod !
  PROJECT_ID: "TON_PROJECT_ID"

handlers:
  - url: /.*
    script: auto
```

---

## GitHub Actions — PROD (approbation obligatoire)
```yaml
name: "Deploy PROD"
on:
  push:
    branches: [ main ]    # ← seulement main → prod

jobs:
  terraform-apply:
    runs-on: ubuntu-latest
    environment: production   # ← protection GitHub requis approbation !
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER_PROD }}
          service_account: ${{ secrets.WIF_SA_PROD }}
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: terraform
      - run: terraform apply -var="project_id=${{ secrets.GCP_PROJECT_ID_PROD }}" -var="environment=prod" -auto-approve
        working-directory: terraform

  deploy-prod:
    needs: terraform-apply
    runs-on: ubuntu-latest
    environment: production    # ← approbation requise !
    timeout-minutes: 15
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER_PROD }}
          service_account: ${{ secrets.WIF_SA_PROD }}
      - uses: google-github-actions/deploy-appengine@v2
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID_PROD }}
          promote: true
```

---

## Configurer l'approbation GitHub (Protection PROD)

1. GitHub → repo → **Settings → Environments → New environment**
2. Nom : `production`
3. Coche **"Required reviewers"**
4. Ajoute les approbateurs (DevOps lead, Tech lead)
5. Sauvegarde

> 💡 Maintenant chaque déploiement en PROD nécessite une approbation manuelle !

---

## Secrets PROD séparés des secrets DEV

| Secret GitHub | Description |
|--------------|-------------|
| `GCP_PROJECT_ID_PROD` | ID projet production |
| `WIF_PROVIDER_PROD` | WIF provider production |
| `WIF_SA_PROD` | Service Account production |

---

## Checklist PROD obligatoire
- [ ] Testé et validé en DEV d'abord
- [ ] Pull Request approuvée par au moins 1 reviewer
- [ ] `terraform plan` révisé et approuvé
- [ ] Secrets PROD dans Secret Manager (pas en clair)
- [ ] Backup des données activé
- [ ] Alertes monitoring configurées
- [ ] Rollback plan préparé
- [ ] Déploiement pendant les heures creuses
