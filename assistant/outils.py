"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""

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
    return sorted(chemin.name for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"]))


def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # À faire (étape 3) : refuser tout chemin hors du dossier, y compris par .., chemin absolu
    # ou lien symbolique, et toute autre extension que celle des limites.
    raise NotImplementedError("Étape 3 : chemin_autorise")


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # À faire (étape 3) : contrôler le chemin et la taille, puis lire la fiche.
    raise NotImplementedError("Étape 3 : lire_fiche")


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    raise NotImplementedError("Étape 4 : ecrire_fiche")


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    # À faire (étape 3) : lire les arguments JSON de appel.function.arguments,
    # puis lancer l’outil nommé appel.function.name ; tout appel invalide est refusé.
    raise NotImplementedError("Étape 3 : executer")
