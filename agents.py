"""
TenderWin - Système multi-agents pour la réponse aux appels d'offres.

Architecture à 3 agents orchestrés séquentiellement :
  1. KnowledgeAgent  → Analyse le RFP et collecte les données internes
  2. WriterAgent     → Rédige la proposition commerciale en Markdown
  3. AuditorAgent    → Audite la proposition (prix, certifications, conformité)

Framework : google-genai
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import get_pricing_catalog, read_company_knowledge

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────

load_dotenv()

# Initialisation du client google-genai. 
# L'API Key est lue automatiquement depuis la variable d'environnement GEMINI_API_KEY.
client = genai.Client()

model_id = os.getenv("MODEL_ID", "gemini-2.5-flash")
# Si l'ID du modèle contient un préfixe litellm (ex: gemini/gemini-2.5-flash), on le nettoie.
if model_id.startswith("gemini/"):
    model_id = model_id.replace("gemini/", "")


# ──────────────────────────────────────────────────────────────
# Outils (Déclarations Python natives pour google-genai)
# ──────────────────────────────────────────────────────────────


def fetch_company_profile() -> str:
    """Récupère le profil complet de l'entreprise TechSecure Solutions.

    Retourne toutes les informations sur l'entreprise : nom, date de création,
    siège social, effectif, mission, certifications (ISO 27001, SOC 2, RGPD),
    SLA, support et clients de référence.

    Utilise cet outil pour obtenir les informations nécessaires à la
    présentation de l'entreprise dans une réponse à un appel d'offres.
    """
    return read_company_knowledge()


def fetch_pricing_catalog() -> str:
    """Récupère le catalogue tarifaire officiel 2026 de TechSecure Solutions.

    Retourne une chaîne au format JSON (une liste d'objets) contenant tous les produits et services avec les clés suivantes :
    - "Produit / Service"
    - "Description"
    - "Prix Unitaire (Annuel)"
    - "Quantité Minimum"

    Produits disponibles : CloudShield Starter, CloudShield Enterprise,
    Module Audit Continu, Support Premium 24/7, Frais d'intégration.

    Utilise cet outil pour calculer un devis ou vérifier les prix officiels. Tu peux utiliser `json.loads()` pour parser la réponse.
    """
    return get_pricing_catalog()


# ──────────────────────────────────────────────────────────────
# System Prompts
# ──────────────────────────────────────────────────────────────

KNOWLEDGE_AGENT_PROMPT = """\
Tu es le **KnowledgeAgent** du système TenderWin. Tu es un analyste expert
en appels d'offres (RFP) dans le domaine de la cybersécurité Cloud.

## Ta mission
Analyser minutieusement le cahier des charges d'un appel d'offres et
collecter **toutes** les informations internes nécessaires pour y répondre.

## Tes responsabilités
1. **Analyser le RFP** : Identifie chaque exigence (technique, fonctionnelle,
   financière, conformité) formulée par le client.
2. **Collecter les données** : Utilise OBLIGATOIREMENT tes outils pour :
   - Récupérer le profil de l'entreprise via `fetch_company_profile`
   - Récupérer le catalogue tarifaire via `fetch_pricing_catalog`
3. **Établir la correspondance** : Pour chaque exigence du client, associe
   les éléments de réponse issus du profil et du catalogue.
4. **Calculer le chiffrage** : Si le client demande un devis, calcule les
   montants exacts en te basant UNIQUEMENT sur le catalogue tarifaire officiel.
   Ne jamais inventer de prix.

## Format de sortie
Produis un rapport structuré contenant :
- La liste des exigences identifiées dans le RFP
- Les informations de l'entreprise correspondant à chaque exigence
- Le calcul détaillé du chiffrage si demandé (formules incluses)
- Les points forts et risques éventuels

## Règles strictes
- Tu ne dois JAMAIS inventer d'informations. Utilise UNIQUEMENT les données
  retournées par tes outils.
- Si une information demandée n'est pas disponible dans les sources, signale-le
  explicitement comme « INFORMATION NON DISPONIBLE ».
- Tous les prix doivent correspondre EXACTEMENT au catalogue tarifaire officiel.
"""

WRITER_AGENT_PROMPT = """\
Tu es le **WriterAgent** du système TenderWin. Tu es un rédacteur commercial
senior spécialisé dans la rédaction de propositions de cybersécurité Cloud
à destination de grands comptes.

## Ta mission
Rédiger une proposition commerciale complète, professionnelle et persuasive
en format Markdown, à partir du rapport d'analyse fourni par le KnowledgeAgent.

## Structure obligatoire de la proposition
Ta proposition DOIT suivre exactement cette structure :

```
# Proposition Commerciale — [Nom du Client]
## 1. Objet de la Proposition
## 2. Présentation de TechSecure Solutions
## 3. Compréhension de Vos Besoins
## 4. Solution Technique Proposée
## 5. Conformité et Certifications
## 6. Engagements de Service (SLA & Support)
## 7. Proposition Financière
## 8. Pourquoi Choisir TechSecure Solutions
## 9. Prochaines Étapes
```

## Règles de rédaction
1. **Ton** : Professionnel, confiant et orienté client. Utilise le vouvoiement.
2. **Certifications** : Mentionne TOUJOURS les certifications ISO 27001,
   SOC 2 Type II et la conformité RGPD dans la section dédiée.
3. **Prix** : Reproduis les prix EXACTEMENT tels qu'ils apparaissent dans
   le rapport du KnowledgeAgent. Ne jamais arrondir ou modifier un prix.
4. **Tableau financier** : La section « Proposition Financière » DOIT contenir
   un tableau Markdown avec les colonnes :
   | Poste | Description | Quantité | Prix Unitaire | Total |
5. **Total** : Calcule et affiche le montant total TTC de la proposition.
6. **Références** : Cite les clients de référence de l'entreprise comme
   preuves de crédibilité.
7. **Longueur** : La proposition doit être complète et détaillée
   (minimum 500 mots).

## Règles strictes
- N'invente AUCUNE information, fonctionnalité ou prix non présent dans
  le rapport d'analyse qui t'est fourni.
- N'ajoute AUCUN produit ou service qui n'apparaît pas dans le catalogue.
- Chaque affirmation doit être traçable aux données du rapport d'analyse.
"""

AUDITOR_AGENT_PROMPT = """\
Tu es l'**AuditorAgent** du système TenderWin. Tu es un auditeur qualité
rigoureux et impartial, spécialisé dans la vérification de propositions
commerciales B2B en cybersécurité.

## Ta mission
Relire et auditer la proposition commerciale rédigée par le WriterAgent.
Tu dois vérifier sa conformité factuelle, tarifaire et réglementaire.

## Checklist d'audit obligatoire

### 1. Vérification tarifaire (CRITIQUE)
- Utilise l'outil `fetch_pricing_catalog` pour récupérer le catalogue officiel.
- Compare CHAQUE prix mentionné dans la proposition avec le catalogue.
- Vérifie que les calculs (quantité × prix unitaire = total) sont exacts.
- Vérifie que le total général est correct.
- Signale toute incohérence tarifaire comme **ERREUR CRITIQUE**.

### 2. Vérification des certifications (CRITIQUE)
- La certification **ISO 27001** DOIT être mentionnée (critère éliminatoire
  dans la plupart des RFP du secteur financier).
- Les certifications **SOC 2 Type II** et **RGPD** doivent être présentes.
- Signale toute certification manquante comme **ERREUR CRITIQUE**.

### 3. Vérification de la structure
- La proposition doit contenir toutes les sections obligatoires.
- Chaque exigence du RFP doit avoir une réponse dans la proposition.

### 4. Vérification de la cohérence
- Les engagements SLA doivent correspondre au profil de l'entreprise (99.99%).
- Les informations sur l'entreprise (effectif, siège, etc.) doivent être exactes.
- Le support 24/7 doit être mentionné si exigé par le client.

## Format du rapport d'audit

```
# Rapport d'Audit — Proposition pour [Nom du Client]

## Résultat Global : ✅ VALIDÉE / ❌ REJETÉE

## Détail des Vérifications

### Tarifs
- [✅/❌] [Produit] : Prix catalogue = X€ | Prix proposition = Y€

### Certifications
- [✅/❌] ISO 27001 : mentionnée / absente
- [✅/❌] SOC 2 Type II : mentionnée / absente
- [✅/❌] RGPD : mentionnée / absente

### Structure & Cohérence
- [✅/❌] Toutes les sections présentes
- [✅/❌] Toutes les exigences du RFP couvertes
- [✅/❌] SLA conforme (99.99%)
- [✅/❌] Support 24/7 mentionné

## Erreurs Critiques
(liste ou "Aucune")

## Recommandations d'Amélioration
(suggestions ou "Aucune")
```

## Règles strictes
- Sois IMPITOYABLE sur les prix : la moindre différence avec le catalogue
  est une erreur critique.
- Ne corrige JAMAIS la proposition toi-même. Signale les erreurs, c'est tout.
- Ton verdict final (VALIDÉE/REJETÉE) doit être binaire, sans compromis.
  Une seule erreur critique entraîne un rejet.
"""


# ──────────────────────────────────────────────────────────────
# Pipeline d'orchestration
# ──────────────────────────────────────────────────────────────

def run_knowledge_agent(gemini_files: list) -> str:
    """Exécute le Knowledge Agent avec les outils associés et l'API Files."""
    config = types.GenerateContentConfig(
        system_instruction=KNOWLEDGE_AGENT_PROMPT,
        tools=[fetch_company_profile, fetch_pricing_catalog],
        temperature=0.2,
    )
    # L'objet chats.create permet de gérer automatiquement les appels d'outils
    # sur plusieurs échanges si le modèle décide de le faire.
    chat = client.chats.create(model=model_id, config=config)
    
    # La payload contient les références aux fichiers Gemini, puis notre instruction textuelle.
    contents = gemini_files + ["Voici le(s) appel(s) d'offres à analyser :"]
    response = chat.send_message(contents)
    return response.text


def run_writer_agent(analyse: str) -> str:
    """Exécute le Writer Agent (sans outils)."""
    config = types.GenerateContentConfig(
        system_instruction=WRITER_AGENT_PROMPT,
        temperature=0.7,
    )
    # Pas d'outils requis, generate_content classique suffit
    response = client.models.generate_content(
        model=model_id,
        contents=(
            "Voici le rapport d'analyse du KnowledgeAgent. "
            "Rédige la proposition commerciale complète en Markdown.\n\n"
            f"--- RAPPORT D'ANALYSE ---\n{analyse}"
        ),
        config=config,
    )
    return response.text


def run_auditor_agent(proposition: str, gemini_files: list) -> str:
    """Exécute l'Auditor Agent avec l'outil de pricing."""
    config = types.GenerateContentConfig(
        system_instruction=AUDITOR_AGENT_PROMPT,
        tools=[fetch_pricing_catalog],
        temperature=0.2,
    )
    chat = client.chats.create(model=model_id, config=config)
    
    contents = gemini_files + [
        f"Voici la proposition commerciale à auditer :\n\n"
        f"--- PROPOSITION ---\n{proposition}\n\n"
        f"Vérifie les prix, les certifications et la conformité aux documents RFP ci-joints."
    ]
    response = chat.send_message(contents)
    return response.text


def run_tender_pipeline(file_paths: list[str]) -> dict:
    """Exécute le pipeline complet de réponse à un appel d'offres.

    Orchestre séquentiellement les 3 agents :
      1. KnowledgeAgent analyse le(s) RFP et collecte les données
      2. WriterAgent rédige la proposition commerciale
      3. AuditorAgent audite la proposition finale

    Gère le cycle de vie des fichiers via la Gemini Files API.

    Args:
        file_paths: Liste des chemins vers les fichiers RFP à traiter.

    Returns:
        dict: Un dictionnaire contenant les clés :
            - 'analyse'    : Le rapport d'analyse du KnowledgeAgent
            - 'proposition': La proposition commerciale en Markdown
            - 'audit'      : Le rapport d'audit de l'AuditorAgent
    """
    print("=" * 60)
    print("🚀 TENDERWIN — Lancement du pipeline (google-genai)")
    print("=" * 60)

    # ── Étape 0 : Upload vers Google GenAI ──
    print("\n☁️  Upload des fichiers vers Gemini...")
    gemini_files = []
    
    try:
        for path in file_paths:
            # Upload du fichier. display_name permet au modèle de l'identifier.
            file_obj = client.files.upload(
                file=path,
                config={'display_name': os.path.basename(path)}
            )
            gemini_files.append(file_obj)
            print(f"   Uploadé : {file_obj.display_name} (URI: {file_obj.uri})")

        # ── Étape 1 : Analyse du RFP ──
        print("\n📋 [1/3] KnowledgeAgent — Analyse en cours...")
        analyse = run_knowledge_agent(gemini_files)
        print("✅ Analyse terminée.\n")

        # ── Étape 2 : Rédaction de la proposition ──
        print("✍️  [2/3] WriterAgent — Rédaction en cours...")
        proposition = run_writer_agent(analyse)
        print("✅ Proposition rédigée.\n")

        # ── Étape 3 : Audit de la proposition ──
        print("🔍 [3/3] AuditorAgent — Audit en cours...")
        audit = run_auditor_agent(proposition, gemini_files)
        print("✅ Audit terminé.\n")

    finally:
        # Nettoyage des fichiers sur l'infrastructure Google
        print("\n🧹 Nettoyage des fichiers distants...")
        for file_obj in gemini_files:
            try:
                client.files.delete(name=file_obj.name)
            except Exception as e:
                print(f"⚠️  Erreur lors de la suppression de {file_obj.name}: {e}")

    # ── Résumé ──
    print("\n" + "=" * 60)
    print("🏁 TENDERWIN — Pipeline terminé avec succès")
    print("=" * 60)

    return {
        "analyse": analyse,
        "proposition": proposition,
        "audit": audit,
    }
