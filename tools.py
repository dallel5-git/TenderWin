"""
TenderWin - Outils (Tools) pour les agents IA.

Ce module fournit les fonctions-outils que les agents LLM peuvent appeler
pour accéder aux données de l'entreprise : profil société et catalogue tarifaire.
"""

import csv
import json
import os

# Répertoire racine du projet (où se trouve ce fichier)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read_company_knowledge() -> str:
    """Lit et retourne le profil complet de l'entreprise TechSecure.

    Cette fonction charge le fichier 'data/profil_techsecure.txt' qui contient
    toutes les informations sur l'entreprise : présentation, domaines d'expertise,
    certifications, références clients et avantages concurrentiels.

    Utilise cet outil lorsque tu as besoin de connaître les compétences,
    l'expérience ou le positionnement de l'entreprise pour rédiger
    une réponse à un appel d'offres.

    Returns:
        str: Le contenu textuel complet du profil de l'entreprise.

    Raises:
        FileNotFoundError: Si le fichier 'data/profil_techsecure.txt' est introuvable.
    """
    filepath = os.path.join(_BASE_DIR, "data", "profil_techsecure.txt")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Le fichier du profil entreprise est introuvable : {filepath}. "
            "Assurez-vous que 'data/profil_techsecure.txt' existe à la racine du projet."
        )


def get_pricing_catalog() -> str:
    """Lit et retourne le catalogue tarifaire 2026 de l'entreprise.

    Cette fonction charge le fichier 'data/tarifs_2026.csv' qui contient
    les tarifs journaliers (TJM) de tous les profils et services proposés
    par l'entreprise, au format CSV.

    Utilise cet outil lorsque tu dois chiffrer une proposition commerciale,
    estimer le coût d'une prestation ou construire un tableau financier
    pour un appel d'offres.

    Returns:
        str: Le contenu brut du fichier CSV des tarifs.

    Raises:
        FileNotFoundError: Si le fichier 'data/tarifs_2026.csv' est introuvable.
    """
    filepath = os.path.join(_BASE_DIR, "data", "tarifs_2026.csv")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return json.dumps(list(reader), ensure_ascii=False, indent=2)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Le catalogue tarifaire est introuvable : {filepath}. "
            "Assurez-vous que 'data/tarifs_2026.csv' existe à la racine du projet."
        )
