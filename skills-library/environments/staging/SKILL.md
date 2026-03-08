---
name: gcp-env-staging
description: >
  Skill configuration environnement STAGING pour GCP App Engine.
  Utilise ce skill quand on configure ou déploie en staging, quand on parle
  de pré-production, UAT (User Acceptance Testing), validation avant prod,
  ou environnement de recette. Toujours combiner avec gcp-security.
  Le staging doit être identique à la prod — c'est le dernier filet de sécurité !
---

# 🧪 Environnement STAGING — Configuration GCP

## ⚠️ Références obligatoires
→ `skills-library/security/SKILL.md` — Sécurité
→ `skills-library/environments/dev/SKILL.md` — Valider en DEV d'abord !

---

## Principe du Staging

```
DEV → STAGING → PROD
        ↑
   Identique à PROD
   mais avec données fictives
   Dernier test avant go-live !
```

---

## Caractéristiques STAGING

| Paramètre | Valeur STAGING | Raison |
|-----------|---------------|--------|
| `max_instances` | 5 | Similaire prod, coût réduit |
| `instance_class` | F2 | Identique à prod |
| `min_idle_instances` | 1 | Simuler comportement prod |
| Déploiement | Semi-automatique | PR approuvée requis |
| Données | Fictives réalistes | Simuler prod sans risque |
| Logs | INFO | Identique à prod |

---

## app.yaml — STAGING
```yaml
runtime: python312
env: standard
instance_class: F2          # ← identique à prod !

automatic_scaling:
  min_idle_instances: 1
  max_idle_instances: 2
  max_instances: 5

env_variables:
  ENVIRONMENT: "staging"
  LOG_LEVEL: "INFO"
  PROJECT_ID: "TON_PROJECT_ID-staging"

handlers:
  - url: /.*
    script: auto
```

---

## GitHub Actions — STAGING
```yaml
name: "Deploy STAGING"
on:
  push:
    branches: [ staging ]    # ← branche staging → déploie en staging

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging     # ← approbation optionnelle
    timeout-minutes: 15
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER_STAGING }}
          service_account: ${{ secrets.WIF_SA_STAGING }}
      - uses: google-github-actions/deploy-appengine@v2
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID_STAGING }}
          promote: true
```

---

## Workflow complet DEV → STAGING → PROD

```
feature/ma-feature
        │ merge
        ▼
    develop  ──────────────→  DEV
        │ PR approuvée         https://TON_PROJECT-dev.appspot.com
        ▼
    staging  ──────────────→  STAGING
        │ tests UAT OK         https://TON_PROJECT-staging.appspot.com
        │ approbation Tech Lead
        ▼
      main   ──────────────→  PROD
                               https://TON_PROJECT.appspot.com
```

---

## Checklist STAGING
- [ ] Validé en DEV d'abord
- [ ] Données fictives (pas de vraies données clients)
- [ ] Tests de performance exécutés
- [ ] Tests UAT complétés par l'équipe QA
- [ ] Approbation Tech Lead obtenue
- [ ] Vérifier que le comportement est identique à prod
