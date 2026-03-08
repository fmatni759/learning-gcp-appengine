---
name: gcp-master-deploy
description: >
  Skill principal GCP — orchestre tous les autres skills pour déployer
  une application complète sur GCP App Engine de façon sécurisée.
  Utilise ce skill quand on commence un nouveau projet GCP, quand une nouvelle
  équipe veut déployer sur GCP, quand on veut le guide complet de déploiement,
  ou quand on ne sait pas quel skill utiliser. Ce skill lit automatiquement
  les skills de sécurité et d'environnement appropriés.
  Déclenche pour : "nouveau projet GCP", "déployer mon app", "setup CI/CD GCP",
  "pipeline complet GCP", "onboarding GCP équipe".
---

# 🎯 Master Deploy — Guide Orchestrateur GCP

## Ce skill relie tous les autres skills

```
gcp-master-deploy (ce fichier)
        │
        ├── 🔒 security/SKILL.md
        │       ├── references/wif-setup.md
        │       ├── references/iam-policies.md
        │       └── references/secrets-management.md
        │
        ├── 🛠️ environments/dev/SKILL.md
        │
        ├── 🧪 environments/staging/SKILL.md
        │
        ├── 🚀 environments/prod/SKILL.md
        │
        └── 📚 gcp-appengine-cicd/SKILL.md
                ├── references/troubleshooting.md
                └── references/file-templates.md
```

---

## ÉTAPE 0 — Lire les skills dans cet ordre

Avant de commencer, Claude doit lire dans cet ordre :
1. `skills-library/security/SKILL.md` — règles non-négociables
2. `skills-library/environments/[dev|staging|prod]/SKILL.md` — selon l'environnement
3. `gcp-appengine-cicd/SKILL.md` — guide technique complet
4. `gcp-appengine-cicd/references/troubleshooting.md` — si erreur

---

## ÉTAPE 1 — Identifier le contexte

Poser ces questions à l'équipe :

```
1. Quel environnement ? (dev / staging / prod)
2. Nouveau projet ou existant ?
3. Quel langage ? (Python / Node.js / Java / Go)
4. Compte GCP disponible ?
5. Repo GitHub existant ?
6. Workload Identity déjà configuré ?
```

---

## ÉTAPE 2 — Checklist de démarrage

### Nouveau projet — Faire UNE SEULE FOIS

```bash
# 1. Créer le projet GCP (via portail console.cloud.google.com)

# 2. Activer les APIs
gcloud services enable \
  appengine.googleapis.com \
  cloudbuild.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  artifactregistry.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  --project=TON_PROJECT_ID

# 3. Créer App Engine (portail GCP → App Engine → Create)
# Région : northamerica-northeast1 (Montréal)

# 4. Créer bucket Terraform remote state
gcloud storage buckets create gs://TON_PROJECT_ID-tfstate \
  --location=northamerica-northeast1

# 5. Configurer Workload Identity
# → Voir security/references/wif-setup.md

# 6. Configurer secrets GitHub
# → GCP_PROJECT_ID, WIF_PROVIDER, WIF_SERVICE_ACCOUNT
```

---

## ÉTAPE 3 — Structure de repo standard

```
mon-app/
├── .github/
│   └── workflows/
│       ├── terraform-plan.yml    ← PR → plan
│       ├── deploy-dev.yml        ← push develop → DEV
│       ├── deploy-staging.yml    ← push staging → STAGING
│       └── deploy-prod.yml       ← push main → PROD (approuvé)
├── terraform/
│   ├── providers.tf
│   ├── variables.tf
│   ├── main.tf                   ← APIs seulement, PAS app engine !
│   └── outputs.tf
├── skills-library/               ← skills de l'équipe
│   ├── security/
│   ├── environments/
│   └── master-deploy/
├── main.py
├── app.yaml
├── requirements.txt
└── .gitignore                    ← key.json TOUJOURS ignoré
```

---

## ÉTAPE 4 — Workflow Git de l'équipe

```
Développeur crée feature/ma-feature
        │
        ▼
git push → Pull Request vers develop
        │ terraform plan automatique en commentaire PR
        │ Review par un collègue
        ▼
Merge develop → déploiement auto DEV ✅
        │
        ▼
Tests OK en DEV → PR develop vers staging
        │ approbation Tech Lead
        ▼
Merge staging → déploiement auto STAGING ✅
        │
        ▼
Tests UAT OK → PR staging vers main
        │ approbation obligatoire (DevOps Lead)
        │ terraform plan révisé
        ▼
Merge main → déploiement PROD ✅
```

---

## ÉTAPE 5 — URLs par environnement

| Environnement | URL |
|--------------|-----|
| DEV | `https://TON_PROJECT_ID-dev.nn.r.appspot.com` |
| STAGING | `https://TON_PROJECT_ID-staging.nn.r.appspot.com` |
| PROD | `https://TON_PROJECT_ID.nn.r.appspot.com` |

---

## ÉTAPE 6 — Secrets GitHub par environnement

| Secret | DEV | STAGING | PROD |
|--------|-----|---------|------|
| `GCP_PROJECT_ID` | `-dev` | `-staging` | prod |
| `WIF_PROVIDER` | pool dev | pool staging | pool prod |
| `WIF_SERVICE_ACCOUNT` | sa-dev | sa-staging | sa-prod |

> 💡 Chaque environnement a son propre projet GCP et ses propres secrets !

---

## En cas d'erreur

Consulter dans cet ordre :
1. `gcp-appengine-cicd/references/troubleshooting.md` — 13 erreurs connues
2. Logs Cloud Build : `console.cloud.google.com/cloud-build`
3. Logs App Engine : `console.cloud.google.com/appengine`

---

## Onboarding nouvelle équipe — Checklist

- [ ] Partager ce repo GitHub avec l'équipe
- [ ] Chaque dev lit `security/SKILL.md` en premier
- [ ] Créer les projets GCP (dev, staging, prod)
- [ ] Configurer WIF pour chaque environnement
- [ ] Configurer secrets GitHub par environnement
- [ ] Premier déploiement test en DEV ensemble
- [ ] Valider le workflow PR → DEV → STAGING → PROD
