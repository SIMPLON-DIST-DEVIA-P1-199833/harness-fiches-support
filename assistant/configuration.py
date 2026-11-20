"""Configuration de l’assistant : service d’IA dans .env, limites dans limites.toml."""

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

# __file__ : chemin de ce fichier ; resolve() le rend absolu, chaque .parent remonte d’un dossier.
RACINE = Path(__file__).resolve().parent.parent


# Exception propre au projet : raise ConfigurationInvalide("message"), puis except ConfigurationInvalide.
class ConfigurationInvalide(Exception):
    """La configuration ne permet pas de démarrer l’assistant."""


# Entre deux Path, ou un Path et une chaîne, / assemble un chemin.
def charger_limites(chemin=RACINE / "limites.toml"):
    """Renvoie les limites de limites.toml dans un dictionnaire."""
    with open(
        chemin, "rb"
    ) as fichier:  # "rb" : lecture en binaire, demandée par tomllib
        limites = tomllib.load(fichier)
    limites["dossier_fiches"] = RACINE / limites["dossier_fiches"]
    return limites


def charger_configuration():
    """Lit .env et renvoie la configuration du service d’IA dans un dictionnaire."""
    load_dotenv(RACINE / ".env")
    service = os.getenv(
        "SERVICE", "litellm"
    )  # variable d’environnement SERVICE, sinon "litellm"
    if service == "simule":
        return {"service": "simule", "modele": "simule"}

    # À faire (étape 1) : lire LITELLM_API_KEY, LITELLM_BASE_URL et MODELE ;
    # recuperation de variable du .env
    url = os.getenv("LITELLM_BASE_URL")
    cle = os.getenv("LITELLM_API_KEY")
    modele = os.getenv("MODELE")

    # lever ConfigurationInvalide avec un message qui dit quoi faire si la clé ou l’adresse manque ;
    if not url or not cle or not modele:
        manquants = []
        if not url:
            manquants.append("LITELLM_BASE_URL")
        if not cle:
            manquants.append("LITELLM_API_KEY")
        if not modele:
            manquants.append("MODELE")
        raise ConfigurationInvalide(
            f"Configuration manquante : les variables {', '.join(manquants)} doivent être définies dans le fichier .env"
        )
    # raise NotImplementedError("Étape 1 : charger_configuration")
    # renvoyer {"service": "litellm", "url": ..., "cle": ..., "modele": ...}.
    return {"service": "litellm", "url": url, "cle": cle, "modele": modele}
