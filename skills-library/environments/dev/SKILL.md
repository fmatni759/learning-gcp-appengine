---
name: gcp-env-dev
description: >
  Skill configuration environnement DEV pour GCP App Engine.
  Utilise ce skill quand on configure ou déploie en environnement de développement,
  quand on parle de config dev, de tests, de sandbox GCP, ou quand on crée
  un nouvel environnement de développement. Toujours combiner avec gcp-security.
---

# 🛠️ Environnement DEV — Configuration GCP

## ⚠️ Référence Sécurité obligatoire
Avant toute configuration, lire et appliquer :
→ `skills-library/security/SKILL.md`

---

## Caractéristiques DEV

| Paramètre | Valeur DEV | Raison |
|-----------|-----------|--------|
| `max_instances` | 2 | Économiser les coûts |
| `instance_class` | F1 | Minimum suffisant pour tests |
| `min_idle_instances` | 0 | Scale to zero — pas de coût idle |
| Déploiement | Automatique | Pas d'approbation requise |
| Données | Fictives seulement | Jamais de données réelles |
| Logs | Verbeux (DEBUG) | Facilite le debugging |

---

## app.yaml — DEV
```yaml
runtime: python312
env: standard
instance_class: F1

automatic_scaling:
  min_idle_instances: 0
  max_idle_instances: 1
  max_instances: 2        # ← faible pour économiser

env_variables:
  ENVIRONMENT: "dev"
  LOG_LEVEL: "DEBUG"
  PROJECT_ID: "TON_PROJECT_ID-dev"

handlers:
  - url: /.*
    script: auto
```

---

## terraform/variables-dev.tfvars
```hcl
project_id  = "TON_PROJECT_ID-dev"
region      = "northamerica-northeast1"
environment = "dev"
```

---

## GitHub Actions — DEV (déploiement automatique)
```yaml
name: "Deploy DEV"
on:
  push:
    branches: [ develop ]   # ← branche develop → déploie en DEV

jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER_DEV }}
          service_account: ${{ secrets.WIF_SA_DEV }}
      - uses: google-github-actions/deploy-appengine@v2
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID_DEV }}
          promote: true
```

---

## Workflow DEV jour-à-jour

```
git checkout -b feature/ma-feature
        │ coder + tester localement
        ▼
git push origin feature/ma-feature
        │ Pull Request vers develop
        ▼
Merge vers develop
        │ déploiement auto en DEV
        ▼
Tester sur https://TON_PROJECT_ID-dev.nn.r.appspot.com
        │ tout fonctionne ?
        ▼
Pull Request develop → main
        │ déploiement en PROD
        ▼
```

---

## Checklist DEV
- [ ] Utiliser des données fictives seulement
- [ ] Project ID séparé du prod (`-dev` suffix)
- [ ] Secrets DEV séparés des secrets PROD
- [ ] Coûts surveillés (budget alert à $10/mois)
