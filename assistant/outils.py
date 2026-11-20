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
    # À faire (étape 4) : décrire l’outil ecrire_fiche.
]


class AccesRefuse(Exception):
    """Une limite fixée par l’équipe interdit l’opération demandée."""


def lister_fiches(limites):
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(chemin.name for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"]))


def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    dossier = Path(limites["dossier_fiches"]).resolve()
    chemin = (dossier / nom).resolve()
    if not chemin.is_relative_to(dossier):
        raise AccesRefuse(f"Refusé : {nom} est hors du dossier des fiches.")
    if chemin.suffix != limites["extension"]:
        raise AccesRefuse(f"Refusé : {nom} n’est pas un fichier {limites['extension']}.")
    return chemin


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    chemin = chemin_autorise(nom, limites)
    if not chemin.is_file():
        raise AccesRefuse(f"Refusé : la fiche {nom} n’existe pas.")
    if chemin.stat().st_size > limites["taille_max_ko"] * 1024:
        raise AccesRefuse(f"Refusé : {nom} dépasse {limites['taille_max_ko']} Ko.")
    return chemin.read_text(encoding="utf-8")


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    raise NotImplementedError("Étape 4 : ecrire_fiche")


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    try:
        arguments = json.loads(appel.function.arguments)
    except json.JSONDecodeError:
        raise AccesRefuse(f"Refusé : arguments mal formés pour {appel.function.name}.")
    try:
        if appel.function.name == "lire_fiche":
            return lire_fiche(arguments["nom"], limites)
    except (KeyError, TypeError):  # KeyError : argument absent ; TypeError : arguments qui ne sont pas un dictionnaire
        raise AccesRefuse(f"Refusé : arguments incomplets pour {appel.function.name}.")
    raise AccesRefuse(f"Refusé : l’outil {appel.function.name} n’existe pas.")
