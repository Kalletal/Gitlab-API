# GitLab Explorer

Interface TUI (Terminal User Interface) pour déclencher des pipelines GitLab depuis une collection Insomnia.

## Description

GitLab Explorer est un outil en ligne de commande avec interface visuelle qui permet de :

- Charger une collection Insomnia au format YAML
- Sélectionner un environnement de déploiement (datacenter, cluster vSphere...)
- Modifier les variables de déploiement à la volée
- Déclencher un pipeline GitLab via l'API REST

Cet outil est destiné aux équipes infrastructure pour automatiser le déploiement de VMs via Terraform/GitLab CI.

## Prérequis

- Python 3.13+
- Un fichier de collection Insomnia exporté au format YAML (version 5.0+)
- Un token de trigger GitLab (`glptt-...`) dans la collection
- Accès réseau à l'instance GitLab cible

## Installation

### 1. Cloner le projet

```bash
git clone https://gitlab.swmcloud.net/ton-projet/gitlab-explorer.git
cd gitlab-explorer
```

### 2. Créer l'environnement virtuel

```bash
python3.13 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```
GITLAB_URL=https://gitlab.swmcloud.net
GITLAB_PROJECT_ID=2011
```

> ⚠️ Ne jamais committer le fichier `.env` — il est exclu par le `.gitignore`

## Utilisation

```bash
python main.py
```

### Premier lancement

Au premier lancement, un sélecteur de fichier s'ouvre pour choisir la collection Insomnia. Le chemin est sauvegardé dans `config.yaml` pour les lancements suivants.

### Interface

```
┌─ gitlabapi ──────────────────────────────────────────┐
│                                                       │
│  Environnements          │  Variables                 │
│  ──────────────────────  │  ─────────────────────     │
│  > CRBV - DC-INFRA       │  token : [glptt-xxxx  ]   │
│    CRBV - Prod-CRBV      │  DATACENTER : [hci_inf]   │
│    DEV - dev-infra       │  VM_CPU : [4          ]   │
│    HCI-INFRA - DC-INFRA  │  VM_RAM : [12288      ]   │
│    HCI-PROD - DC-PROD    │  ...                      │
│                                                       │
│                    [ Déployer ]                       │
└───────────────────────────────────────────────────────┘
```

### Raccourcis clavier

| Touche | Action |
|--------|--------|
| `C` | Changer de fichier de collection |
| `Q` | Quitter |
| `Tab` | Naviguer entre les widgets |
| `Entrée` | Sélectionner un environnement |

### Changer de collection

Appuyer sur `C` pour ouvrir le sélecteur de fichier et charger une autre collection.

## Structure du projet

```
gitlab-explorer/
├── .env                  # Variables d'environnement (non commité)
├── .gitignore
├── README.md
├── requirements.txt
├── config.yaml           # Chemin vers la collection active (généré automatiquement)
├── debug.log             # Logs de débogage (généré automatiquement)
└── main.py               # Script principal
```

## Variables de déploiement

| Variable | Description |
|----------|-------------|
| `token` | Token de trigger GitLab (`glptt-...`) |
| `CML` | Hostname court du serveur à déployer |
| `DATACENTER` | Datacenter cible (`crbv` / `stdn` / `dev` / `hci_dev` / `hci_prod` / `hci_infra`) |
| `VM_CPU` | Nombre de CPUs (entre 2 et 10) |
| `VM_RAM` | RAM en Mo — puissance de 2, entre 2048 et 12288 |
| `VM_VSPHERE_DC` | Nom du Datacenter vSphere |
| `VM_VSPHERE_CLUSTER` | Nom du cluster vSphere |
| `VM_VSPHERE_DATASTORE` | Nom du datastore vSphere (HCI) |
| `VM_VSPHERE_DATASTORE_CLUSTER` | Nom du cluster de datastore vSphere |
| `VM_NETWORK` | Nom du réseau vSphere |
| `VM_IPAM_SUBNET` | Nom du subnet IPAM correspondant |
| `VM_TEMPLATE` | Chemin complet vers le template vSphere |
| `VM_FOLDER` | Chemin vers le dossier vSphere de destination |
| `VM_ADDITIONAL_DISKS` | Disques supplémentaires au format `1-10;2-50` |
| `DESTROY` | Mettre `TRUE` pour détruire une VM provisionnée |

## Dépendances

```
textual>=8.1.1
pyyaml
requests
python-dotenv
```

## Notes

- Les variables préremplies viennent de l'environnement sélectionné dans la collection Insomnia
- Toutes les variables sont modifiables avant le déclenchement du pipeline
- Le token `glptt-...` doit être celui du projet GitLab cible, pas un Personal Access Token
- Les logs de débogage sont écrits dans `debug.log`

## Auteur

Gilles Dalmas — Softway Medical
