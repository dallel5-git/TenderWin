"""
TenderWin — Point d'entrée principal.

Lance le pipeline multi-agents pour générer une réponse complète
à un appel d'offres (RFP) et sauvegarde les résultats.

Usage :
    python main.py
    python main.py --rfp data/RFP_Financo_2026.txt
    python main.py --rfp data/RFP_Financo_2026.txt --output mon_dossier
"""

import argparse
import os
import sys
from datetime import datetime

# Répertoire racine du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read_rfp(rfp_filepath: str) -> str:
    """Lit et retourne le contenu d'un fichier d'appel d'offres.

    Args:
        rfp_filepath: Chemin vers le fichier RFP (absolu ou relatif au projet).

    Returns:
        str: Le contenu textuel du RFP.

    Raises:
        FileNotFoundError: Si le fichier RFP n'existe pas.
        ValueError: Si le fichier RFP est vide.
    """
    # Résoudre le chemin relatif par rapport à la racine du projet
    if not os.path.isabs(rfp_filepath):
        rfp_filepath = os.path.join(BASE_DIR, rfp_filepath)

    if not os.path.exists(rfp_filepath):
        raise FileNotFoundError(
            f"❌ Fichier RFP introuvable : {rfp_filepath}\n"
            f"   Vérifiez le chemin et réessayez."
        )

    with open(rfp_filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(
            f"❌ Le fichier RFP est vide : {rfp_filepath}\n"
            f"   Le fichier doit contenir le texte de l'appel d'offres."
        )

    return content


def process_rfp_files(file_paths: list[str]) -> dict:
    """Exécute le pipeline multi-agents à partir d'une liste de fichiers (RFP).

    Cette fonction est le cœur du workflow. Elle peut être appelée
    directement depuis l'interface Streamlit ou depuis process_rfp().

    Workflow séquentiel :
      1. KnowledgeAgent → analyse le(s) RFP et collecte les données internes
      2. WriterAgent    → rédige la proposition commerciale en Markdown
      3. AuditorAgent   → audite la conformité (prix, certifications)

    Args:
        file_paths: Liste des chemins vers les fichiers RFP.

    Returns:
        dict: Un dictionnaire contenant les clés :
            - 'analyse'    : Le rapport d'analyse du KnowledgeAgent
            - 'proposition': La proposition commerciale en Markdown
            - 'audit'      : Le rapport d'audit de l'AuditorAgent

    Raises:
        ValueError: Si la liste de fichiers est vide.
    """
    if not file_paths:
        raise ValueError("❌ Aucun fichier RFP n'a été fourni.")

    # Import différé pour isoler la config et éviter le chargement
    # des modèles LLM tant qu'on n'en a pas besoin
    from agents import run_tender_pipeline

    return run_tender_pipeline(file_paths)


def process_rfp(rfp_filepaths: list[str], output_dir: str = "output") -> dict:
    """Exécute le workflow complet de réponse à un appel d'offres.

    Vérifie les fichiers RFP, exécute le pipeline multi-agents, et
    sauvegarde les résultats dans le dossier de sortie.

    Args:
        rfp_filepaths: Liste des chemins vers les fichiers d'appel d'offres.
        output_dir: Dossier de sortie pour les fichiers générés (défaut: 'output').

    Returns:
        dict: Les résultats du pipeline (analyse, proposition, audit).
    """
    # ── Étape 0 : Vérification des RFP ──
    print("\n" + "═" * 60)
    print("  🏆  TENDERWIN — Système de Réponse aux Appels d'Offres")
    print("═" * 60)

    valid_paths = []
    for path in rfp_filepaths:
        # Résoudre le chemin relatif par rapport à la racine du projet
        if not os.path.isabs(path):
            path = os.path.join(BASE_DIR, path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Fichier RFP introuvable : {path}")
        valid_paths.append(path)
        print(f"📄 RFP sélectionné : {os.path.basename(path)}")

    # ── Exécution du pipeline multi-agents ──
    results = process_rfp_files(valid_paths)

    # ── Sauvegarde des résultats ──
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(BASE_DIR, output_dir)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Fichier 1 : Proposition finale (ce que le client verra)
    proposition_path = os.path.join(output_dir, "proposition_finale.md")
    with open(proposition_path, "w", encoding="utf-8") as f:
        f.write(str(results["proposition"]))

    # Fichier 2 : Rapport d'audit (usage interne)
    audit_path = os.path.join(output_dir, f"audit_{timestamp}.md")
    with open(audit_path, "w", encoding="utf-8") as f:
        f.write(str(results["audit"]))

    # Fichier 3 : Rapport d'analyse brut (usage interne)
    analyse_path = os.path.join(output_dir, f"analyse_{timestamp}.md")
    with open(analyse_path, "w", encoding="utf-8") as f:
        f.write(str(results["analyse"]))

    # ── Résumé final ──
    print("\n" + "═" * 60)
    print("  📁  FICHIERS GÉNÉRÉS")
    print("═" * 60)
    print(f"\n  📝 Proposition finale : {proposition_path}")
    print(f"  🔍 Rapport d'audit   : {audit_path}")
    print(f"  📋 Rapport d'analyse : {analyse_path}")
    print()

    return results


def main():
    """Point d'entrée CLI avec parsing des arguments."""
    parser = argparse.ArgumentParser(
        description="TenderWin — Génération automatique de réponses aux appels d'offres",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemples :\n"
            "  python main.py\n"
            "  python main.py --rfp data/RFP_Financo_2026.txt\n"
            "  python main.py --rfp mon_rfp.txt --output resultats/\n"
        ),
    )
    parser.add_argument(
        "--rfp",
        type=str,
        nargs="+",
        default=["data/RFP_Financo_2026.txt"],
        help="Chemin(s) vers le(s) fichier(s) d'appel d'offres (défaut: data/RFP_Financo_2026.txt)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Dossier de sortie pour les fichiers générés (défaut: output/)",
    )

    args = parser.parse_args()

    try:
        process_rfp(rfp_filepaths=args.rfp, output_dir=args.output)
    except (FileNotFoundError, ValueError) as e:
        print(f"\n{e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrompu par l'utilisateur.")
        sys.exit(130)


if __name__ == "__main__":
    main()
