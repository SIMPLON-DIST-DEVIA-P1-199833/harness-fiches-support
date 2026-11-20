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
    {
        "type": "function",
        "function": {
            "name": "ecrire_fiche",
            "description": "Enregistre ou modifie une fiche de procédure en Markdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {
                        "type": "string",
                        "description": "Nom du fichier, par exemple modifier-taux-tva.md",
                    },
                    "contenu": {
                        "type": "string",
                        "description": "Le contenu Markdown de la fiche à enregistrer.",
                    },
                },
                "required": ["nom", "contenu"],
            },
        },
    },
]
# À faire (étape 4) : décrire l’outil ecrire_fiche.


class AccesRefuse(Exception):
    """Une limite fixée par l’équipe interdit l’opération demandée."""


def lister_fiches(limites):
    """Renvoie les noms des fiches du dossier, triés."""
    # Comme une compréhension de liste, sans crochets : sorted reçoit directement chaque nom.
    return sorted(
        chemin.name
        for chemin in Path(limites["dossier_fiches"]).glob("*" + limites["extension"])
    )


def chemin_autorise(nom, limites):
    """Renvoie le chemin de la fiche si elle reste dans le dossier des fiches, sinon lève AccesRefuse."""
    # À faire (étape 3) : refuser tout chemin hors du dossier, y compris par .., chemin absolu
    dossier_autorise = Path(limites["dossier_fiches"]).resolve()
    chemin_nom = Path(nom)

    if chemin_nom.is_absolute():
        chemin_demande = chemin_nom.resolve()
    else:
        chemin_demande = (dossier_autorise / chemin_nom).resolve()

    if not chemin_demande.is_relative_to(dossier_autorise):
        raise AccesRefuse(f"Chemin hors du dossier autorisé : {nom}")

    return chemin_demande
    # ou lien symbolique, et toute autre extension que celle des limites.
    # raise NotImplementedError("Étape 3 : chemin_autorise")


def lire_fiche(nom, limites):
    """Renvoie le contenu de la fiche, ou lève AccesRefuse."""
    # À faire (étape 3) : contrôler le chemin et la taille, puis lire la fiche.
    # raise NotImplementedError("Étape 3 : lire_fiche")
    chemin = chemin_autorise(nom, limites)
    if not chemin.exists():
        raise AccesRefuse(f"La fiche '{nom}' n'existe pas.")
    if chemin.suffix != limites["extension"]:
        raise AccesRefuse(
            f"Extension non autorisée. Seuls les fichiers {limites['extension']} sont acceptés."
        )
    taille = chemin.stat().st_size / 1024
    if taille > limites["taille_max_ko"]:
        raise AccesRefuse(
            f"La fiche est trop volumineuse (max {limites['taille_max_ko']} ko)."
        )
    return chemin.read_text(encoding="utf-8")


def ecrire_fiche(nom, contenu, limites, confirmer):
    """Enregistre la fiche ; confirmer(nom) décide d’un écrasement. Lève AccesRefuse sinon."""
    # À faire (étape 4) : contrôler le chemin et la taille, demander confirmation avant d’écraser.
    # raise NotImplementedError("Étape 4 : ecrire_fiche")
    chemin = chemin_autorise(nom, limites)
    if chemin.exists():
        if not confirmer(str(chemin)):
            raise AccesRefuse("L'utilisateur a refusé d'écraser la fiche.")

    taille = len(contenu.encode("utf-8")) / 1024
    if taille > limites["taille_max_ko"]:
        raise AccesRefuse(
            f"Le contenu est trop volumineux (max {limites['taille_max_ko']} ko)."
        )

    chemin.write_text(contenu, encoding="utf-8")
    return f"La fiche '{nom}' a été enregistrée avec succès."


def executer(appel, limites, confirmer):
    """Exécute un appel d’outil du modèle et renvoie le texte de son résultat, ou lève AccesRefuse."""
    # À faire (étape 3) : lire les arguments JSON de appel.function.arguments,
    # puis lancer l’outil nommé appel.function.name ; tout appel invalide est refusé.
    try:
        arguments = json.loads(appel.function.arguments)
    except (json.JSONDecodeError, TypeError):
        raise AccesRefuse("Arguments JSOn invalides.")

    nom_outil = appel.function.name

    if nom_outil == "lire_fiche":
        nom = arguments.get("nom")
        if not nom:
            raise AccesRefuse("Nom de fiche non renseigner")
        return lire_fiche(nom, limites)

    elif nom_outil == "ecrire_fiche":
        nom = arguments.get("nom")
        contenu = arguments.get("contenu")
        if not nom or not contenu:
            raise AccesRefuse("Le nom et le contenu de la fiche sont requis.")
        return ecrire_fiche(nom, contenu, limites, confirmer)

    else:
        raise AccesRefuse(f"L'outil '{nom_outil}' n'est pas supporté.")
    # raise NotImplementedError("Étape 3 : executer")
