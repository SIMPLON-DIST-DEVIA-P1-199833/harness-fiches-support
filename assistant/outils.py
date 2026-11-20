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
                "properties": {
                    "nom": {
                        "type": "string",
                        "description": "Nom du fichier, par exemple modifier-taux-tva.md",
                    }
                },
                "required": ["nom"],
            },
        },
    }
]


class AccesRefuse(Exception):
    """Une limite fixée par l’équipe interdit l’opération demandée."""


def lister_fiches(limites) -> list[Path]:
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(
        chemin.name
        for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"])
    )


def chemin_autorise(nom, limites) -> str:
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # À faire (étape 3) : refuser tout chemin hors du dossier, y compris par .., chemin absolu

    dossier = Path(limites["dossier_fiches"]).resolve()
    demande = Path(nom)

    if demande.is_absolute():
        raise AccesRefuse("Chemin absolu interdit.")

    chemin = (dossier / demande).resolve()

    if not chemin.is_relative_to(dossier):
        raise AccesRefuse("Accès hors du dossier interdit.")

    if chemin.suffix != limites["extension"]:
        raise AccesRefuse("Extension interdite.")
    if nom in lister_fiches(limites):
        return str(limites["dossier_fiches"] / nom)

    raise AccesRefuse("Accés Refuse")


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # À faire (étape 3) : contrôler le chemin et la taille, puis lire la fiche.
    chemin = chemin_autorise(nom, limites)  # lève AccesRefuse
    try:
        with open(chemin, "r") as file:
            # todo: taille de fichier
            return file.read()
    except:
        raise AccesRefuse("Problème ouverture fiche")


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    # À faire (étape 3) : lire les arguments JSON de appel.function.arguments,
    # puis lancer l’outil nommé appel.function.name ; tout appel invalide est refusé.
    try:
        arguments = json.loads(appel.function.arguments)
    except (json.JSONDecodeError, TypeError):
        raise AccesRefuse(
            f"Refus : arguments JSON mal formés pour la fonction {appel.function.name}"
        )

    try:
        if appel.function.name == "lire_fiche":
            return lire_fiche(arguments["nom"], limites)
    except (KeyError, TypeError):
        raise AccesRefuse(
            f"Refus : les arguments pour la fonction {appel.function.name} sont incorrects ou incomplets."
        )

    raise AccesRefuse(f"L’outil {appel.function.name} est inconnu.")
