# TenderWin 🏆

TenderWin est un système automatisé intelligent de réponses aux appels d'offres (RFP), propulsé par une architecture multi-agents.

Le système s'appuie sur le framework Google GenAI (`google-genai`) et utilise le modèle `gemini-2.5-flash` pour analyser les appels d'offres, croiser les données internes de l'entreprise (profil, certifications, catalogue tarifaire) et rédiger une proposition commerciale pertinente, précise et dûment auditée.

## Architecture Multi-Agents 🤖

L'application orchestre séquentiellement trois agents :

1. **KnowledgeAgent** 📋 : Analyse minutieusement le cahier des charges de l'appel d'offres (RFP) et collecte toutes les informations internes pertinentes (profil de l'entreprise, SLA, tarifs) grâce à des outils (tools) spécifiques.
2. **WriterAgent** ✍️ : Rédige une proposition commerciale complète, professionnelle et structurée en Markdown à partir de l'analyse produite par le premier agent.
3. **AuditorAgent** 🔍 : Relit et audite la proposition de façon stricte. Il vérifie l'exactitude absolue des tarifs proposés par rapport au catalogue officiel et s'assure de la présence des certifications requises (ISO 27001, SOC 2, RGPD).

## Structure du Projet 📁

- `app.py` : L'interface web propulsée par Streamlit pour une utilisation interactive.
- `main.py` : Le point d'entrée CLI pour exécuter le pipeline de traitement depuis le terminal.
- `agents.py` : La définition des prompts systèmes, de l'orchestration des agents et des appels à l'API Google GenAI.
- `tools.py` : Les outils factices/mockés permettant aux agents d'accéder aux données de l'entreprise (catalogue, profil).
- `data/` : Dossier destiné à contenir les fichiers d'appels d'offres (ex. fichiers texte, PDF ou Word).
- `requirements.txt` : Les dépendances Python du projet.

## Prérequis ⚙️

- Python 3.10 ou supérieur
- Une clé d'API Google Gemini (via [Google AI Studio](https://aistudio.google.com/))

## Installation 🚀

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-nom/tenderwin_project.git
   cd tenderwin_project
   ```

2. **Créer un environnement virtuel et l'activer**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   Créez un fichier `.env` à la racine du projet et ajoutez votre clé API Gemini :
   ```env
   GEMINI_API_KEY=votre_cle_api_ici
   MODEL_ID=gemini-2.5-flash
   ```

## Utilisation 💡

### Via l'interface web (Streamlit)
L'interface Streamlit offre une expérience visuelle pour glisser-déposer vos fichiers RFP et afficher la proposition commerciale générée.
```bash
streamlit run app.py
```

### Via la ligne de commande (CLI)
Vous pouvez également lancer l'outil de manière automatisée dans le terminal :
```bash
python main.py --rfp data/votre_rfp.txt --output resultats/
```

## Licence 📄
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
