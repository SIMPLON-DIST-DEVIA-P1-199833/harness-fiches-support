"""Outils proposés au modèle : lire et écrire une fiche, dans les limites fixées."""

import json
import os.path
from collections.abc import Callable
from pathlib import Path

from .configuration import RACINE, Limites

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
    {
        "type": "function",
        "function": {
            "name": "ecrire_fiche",
            "description": "Ecrit une fiche de procédure en Markdown et indique si elle a bien été écrite. L'assistant aura le dernier mot sur la réécriture ou non d'un fichier existant, par un sous-appel déjà inclut dans cet outil.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {
                        "type": "string",
                        "description": "Le nom du fichier à écrire, par exemple modifier-taux-tva.md",
                    },
                    "contenu": {
                        "type": "string",
                        "description": "Contenu Markdown du fichier à écrire",
                    },
                },
                "required": ["nom", "contenu"],
            },
        },
    },
]


class AccesRefuse(Exception):
    """Une limite fixée par l’équipe interdit l’opération demandée."""


def noms_fonctions(definitions):
    return [definition["function"]["name"] for definition in definitions]


def lister_fiches(limites: Limites):
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(
        chemin.name
        for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"])
    )


def chemin_autorise(nom: str, limites: Limites, pour_ecriture: bool = False) -> Path:
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # À faire (étape 3) : refuser tout chemin hors du dossier, y compris par .., chemin absolu
    # ou lien symbolique, et toute autre extension que celle des limites.
    chemin_dossier_fiches = RACINE / limites["dossier_fiches"]
    chemin_theorique = chemin_dossier_fiches / nom
    contenu_dans_dossier = chemin_theorique.is_relative_to(chemin_dossier_fiches)

    if pour_ecriture:
        if contenu_dans_dossier:
            return chemin_theorique
        else:
            raise AccesRefuse(f"Chemin de fiche non autorisé pour écriture : {nom}")
    else:
        if contenu_dans_dossier:
            return chemin_theorique
        else:
            raise AccesRefuse(f"Chemin de fiche non autorisé : {nom}")


def lire_fiche(nom: str, limites: Limites) -> str:
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # À faire (étape 3) : contrôler le chemin et la taille, puis lire la fiche.
    try:
        chemin_fiche = chemin_autorise(nom, limites)  # Raises: AccesRefuse
        file_size_ko = os.path.getsize(chemin_fiche) / 1000
        max_size_ko = limites["taille_max_ko"]
        if file_size_ko >= max_size_ko:
            raise AccesRefuse(
                f"Fichier trop volumineux : {nom} ({file_size_ko} ko > {max_size_ko} ko (limite))"
            )
        try:
            with open(chemin_fiche, "r") as fp:
                return fp.read()
        except (OSError, UnicodeError) as e:
            raise AccesRefuse(f"Ouverture impossible du fichier : {nom} ({e})")
    except FileNotFoundError:
        raise AccesRefuse(f"Chemin introuvable : {nom}")


def ecrire_fiche(nom: str, contenu: str, limites: Limites, confirmer: Callable) -> str:
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon. Retourne nom si succès."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    if not str(contenu).strip():
        raise AccesRefuse(
            f"Impossible d'écrire la fiche {nom} car le contenu fourni est vide."
        )
    chemin_fiche = chemin_autorise(
        nom, limites, pour_ecriture=True
    )  # Raises: AccesRefuse
    if chemin_fiche.exists() and not confirmer(nom):
        raise AccesRefuse(
            f"Impossible d'écrire la fiche {nom}, car l'autorisation d'écrasement est négative."
        )
    try:
        with open(chemin_fiche, "w+") as fp:
            fp.write(contenu)
    except (OSError, UnicodeDecodeError) as e:
        raise AccesRefuse(
            f"Impossible de d'écrire la fiche {nom} pour y écrire du contenu. ({e})"
        )
    return nom


def executer(appel, limites: Limites, confirmer: Callable) -> str:
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    # À faire (étape 3) : lire les arguments JSON de appel.function.arguments,
    # puis lancer l’outil nommé appel.function.name ; tout appel invalide est refusé.
    fonction = getattr(appel, "function", None)
    if fonction is not None:
        if fonction.name == "lire_fiche":
            try:
                appel_args = json.loads(fonction.arguments)
            except json.JSONDecodeError as e:
                raise AccesRefuse(
                    f"Appel outil non valide: JSON reçu malformatté ({e})"
                )
            if "nom" in appel_args:
                arg_nom = appel_args["nom"]
                return lire_fiche(arg_nom, limites)
            else:
                raise AccesRefuse("Lire fiche : nom de fichier nom fourni")
        elif fonction.name == "ecrire_fiche":
            try:
                appel_args = json.loads(fonction.arguments)
            except json.JSONDecodeError as e:
                raise AccesRefuse(
                    f"Appel outil non valide: JSON reçu malformatté ({e})"
                )
            if set(appel_args).issuperset({"nom", "contenu"}):
                return ecrire_fiche(
                    appel_args["nom"],
                    appel_args["contenu"],
                    limites,
                    confirmer
                )
            else:
                raise RuntimeError(
                    f"L'appel d'outil 'lire_fiche' par l'IA manque de paramètres pour fonctionner ({len(appel_args)} au lieu de 3)."
                )
        elif fonction.name in noms_fonctions(DEFINITIONS):
            raise AccesRefuse(f"Appel outil non encore géré: {fonction.name}")
        else:
            raise AccesRefuse(f"Appel outil non existant: {fonction.name}")
    else:
        raise RuntimeError("Pas de commande à exécuter")
