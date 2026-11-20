"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""

from pathlib import Path
import json

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
    """Renvoie le chemin de la fiche si elle reste dans le dossier autorisé."""
    dossier = Path(limites["dossier_fiches"]).resolve()
    chemin = (dossier / nom).resolve()

    if not chemin.is_relative_to(dossier):
        raise AccesRefuse("La fiche doit se trouver dans le dossier des fiches.")

    if chemin.suffix != limites["extension"]:
        raise AccesRefuse("La fiche doit avoir l’extension autorisée.")

    return chemin


def lire_fiche(nom, limites):
    """Vérifie la fiche, puis renvoie son contenu."""
    chemin = chemin_autorise(nom, limites)

    if not chemin.is_file():
        raise AccesRefuse("La fiche est introuvable ou ce n’est pas un fichier.")

    taille_max_octets = limites["taille_max_ko"] * 1024
    taille_fiche = chemin.stat().st_size

    if taille_fiche > taille_max_octets:
        raise AccesRefuse("La fiche dépasse la taille autorisée.")

    return chemin.read_text(encoding="utf-8")


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    raise NotImplementedError("Étape 4 : ecrire_fiche")


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle ou lève AccesRefuse."""
    if appel.function.name != "lire_fiche":
        raise AccesRefuse("Outil inconnu.")

    try:
        arguments = json.loads(appel.function.arguments)
    except (json.JSONDecodeError, TypeError) as erreur:
        raise AccesRefuse("Arguments de l’outil invalides.") from erreur

    if not isinstance(arguments, dict):
        raise AccesRefuse("Les arguments doivent être un objet JSON.")

    nom = arguments.get("nom")
    if not isinstance(nom, str) or not nom.strip() or "\x00" in nom:
        raise AccesRefuse("Le nom de la fiche est invalide.")

    return lire_fiche(nom, limites)
