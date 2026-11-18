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


def lister_fiches(limites):
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(
        chemin.name
        for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"])
    )


# See : https://www.stephane-robert.info/docs/developper/programmation/python/pathlib/#normaliser-avec-resolve
# More readable than official python doc


def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # See: https://docs.python.org/fr/3/library/pathlib.html#pathlib.Path.resolve gives absolute path
    try:
        if not isinstance(nom, str) or not nom:
            raise AccesRefuse(
                f"Access refused - {nom} is not a valid type (str) or name"
            )
        folder = Path(limites["dossier_fiches"]).resolve()
        path = (folder / nom).resolve()
        if not path.is_relative_to(folder):
            raise AccesRefuse(f"Acces refused - {nom} outside of the fiches folder")
        # Subfolders not authorized
        if path.parent != folder:
            raise AccesRefuse("Access refused - Subfolders are not allowed")
        if path.suffix != limites["extension"]:
            raise AccesRefuse(
                f"Access refused - only {limites['extension']} files are valid"
            )
    # Catch all in case we are passed bullshit in the name
    except ValueError as error:
        raise AccesRefuse("Access refused - not a valid name :)") from error
    return path


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
