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
    with open(chemin, "rb") as fichier:  # "rb" : lecture en binaire, demandée par tomllib
        limites = tomllib.load(fichier)
    limites["dossier_fiches"] = RACINE / limites["dossier_fiches"]
    return limites


def charger_configuration():
    """Lit .env et renvoie la configuration du service d'IA dans un dictionnaire."""
    load_dotenv(RACINE / ".env")
    service = os.getenv("SERVICE", "litellm")
    if service == "simule":
        return {"service": "simule", "modele": "simule"}
    url = os.getenv("LITELLM_BASE_URL")
    cle_api = os.getenv("LITELLM_API_KEY")
    modele = os.getenv("MODELE")
    if not url:
        raise ConfigurationInvalide(
            "Adresse du service absente : renseignez LITELLM_BASE_URL dans .env."
        )
    if not cle_api:
        raise ConfigurationInvalide(
            "Clé absente : renseignez LITELLM_API_KEY dans .env (ne la versionne jamais)."
        )
    if not modele:
        raise ConfigurationInvalide(
            "Modèle absent : renseignez MODELE dans .env (ex. gpt-luna)."
        )
    return {"service": "litellm", "url": url, "cle": cle_api, "modele": modele}
