"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""

import os.path
from pathlib import Path

from configuration import RACINE, Limites

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
    },
    # À faire (étape 4) : décrire l’outil ecrire_fiche.
]


class AccesRefuse(Exception):
    """Une limite fixée par l’équipe interdit l’opération demandée."""

    def __init__(self, message: str = "") -> None:
        super().__init__()
        self.message = message


def lister_fiches(limites: Limites):
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(
        chemin.name
        for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"])
    )


def chemin_autorise(nom: str, limites: Limites) -> bool:
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # À faire (étape 3) : refuser tout chemin hors du dossier, y compris par .., chemin absolu
    # ou lien symbolique, et toute autre extension que celle des limites.
    return (RACINE / Path(nom)).is_relative_to(Path(limites["dossier_fiches"]))


def lire_fiche(nom: str, limites: Limites) -> str:
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # À faire (étape 3) : contrôler le chemin et la taille, puis lire la fiche.
    try:
        if chemin_autorise(nom, limites):
            if (file_size := os.path.getsize(nom) * 1000) >= (
                max_size := limites["taille_max_ko"]
            ):
                raise AccesRefuse(
                    f"Fichier trop volumineux: {nom} ({file_size} ko > {max_size} ko (limite))"
                )
            with open(nom, "r") as fp:
                return fp.read()
        else:
            raise AccesRefuse(f"Chemin non autorisé: {nom}")
    except FileNotFoundError:
        raise AccesRefuse(f"Chemin introuvable: {nom}")


def ecrire_fiche(nom: str, contenu: str, limites: Limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    raise NotImplementedError("Étape 4 : ecrire_fiche")


def executer(appel, limites: Limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    # À faire (étape 3) : lire les arguments JSON de appel.function.arguments,
    # puis lancer l’outil nommé appel.function.name ; tout appel invalide est refusé.
    raise NotImplementedError("Étape 3 : executer")
