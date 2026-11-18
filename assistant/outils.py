"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""
import json
from pathlib import Path

DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "lire_fiche",
            "description": "Lit une fiche de procédure et renvoie son contenu Markdown.",
            "parameters": {
                "type": "object",
                "properties": {"nom": {"type": "string", "description": "Nom du fichier, par exemple modifier-taux-tva.md"}},
                "required": ["nom"],
            },
        },
    },
    {
            "type": "function",
            "function": {
                "name": "ecrire_fiche",
                "description": "ecrire une fiche de procédure et renvoie son contenu Markdown.",
                "parameters": {
                    "type": "object",
                    "properties": {"nom": {"type": "string", "description": "Nom du fichier, par exemple modifier-taux-tva.md"}},
                    "required": ["nom"],
                },
            },
        }
]


class AccesRefuse(Exception):
    """Une limite fixée par l’équipe interdit l’opération demandée."""


def lister_fiches(limites):
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(chemin.name for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"]))


def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # À faire (étape 3) : refuser tout chemin hors du dossier, y compris par .., chemin absolu
    dossier = Path(limites["dossier_fiches"]).resolve()
    chemin_demande = Path(nom)

    if chemin_demande.is_absolute():
        raise AccesRefuse("Les chemins absolus sont interdits.")

    chemin = (dossier/chemin_demande).resolve()
    # ou lien symbolique, et toute autre extension que celle des limites.
    if not chemin.is_relative_to(dossier):
        raise AccesRefuse("Accès refusé : la fiche doit rester dans le dossier des fiches.")

    if chemin.suffix != limites["extension"]:
        raise AccesRefuse(
            f"Extension interdite : utilise {limites['extension']}."
        )

    return chemin


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # À faire (étape 3) : contrôler le chemin et la taille, puis lire la fiche.
    chemin = chemin_autorise(nom, limites)

    if not chemin.is_file():
        raise AccesRefuse(f"Fiche introuvable : {nom}")

    maximum_autorise = 20 * 1024 
    taille = chemin.stat().st_size
    if taille > maximum_autorise:
        raise AccesRefuse("Fiche trop volumineuse.")
    
    return chemin.read_text(encoding="utf-8")



def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.

    chemin = chemin_autorise(nom, limites)
    taille = len(contenu.encode("utf-8"))
    maximum_autorise = 20 * 1024

    if taille > maximum_autorise:
        raise AccesRefuse("Fiche trop volumineuse : maximum 20 Ko.")

    if chemin.exists():
        if not chemin.is_file():
            raise AccesRefuse("Le chemin ne désigne pas une fiche.")

        if not confirmer(nom):
            raise AccesRefuse("Écrasement refusé : fiche inchangée.")

    chemin.write_text(contenu, encoding="utf-8")
    return f"Fiche enregistrée : {nom}"


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    # À faire (étape 3) : lire les arguments JSON de appel.function.arguments,
    # puis lancer l’outil nommé appel.function.name ; tout appel invalide est refusé.
    try:
        arguments = json.loads(appel.function.arguments)
    except (json.JSONDecodeError, TypeError):
        raise AccesRefuse("Arguments invalides : un objet JSON est attendu.")

    if not isinstance(arguments, dict):
        raise AccesRefuse("Les arguments doivent être un objet JSON.")

    nom_outil = appel.function.name

    if nom_outil == "lire_fiche":
        if set(arguments) != {"nom"}:
            raise AccesRefuse("lire_fiche attend uniquement l’argument nom.")

        if not isinstance(arguments["nom"], str):
            raise AccesRefuse("Le nom de la fiche doit être du texte.")

        return lire_fiche(arguments["nom"], limites)
