"""Configuration de l’assistant : service d’IA dans .env, limites dans limites.toml."""

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parent.parent


class ConfigurationInvalide(Exception):
    """La configuration ne permet pas de démarrer l’assistant."""


def charger_limites(chemin=RACINE / "limites.toml"):
    """Renvoie les limites de limites.toml dans un dictionnaire."""
    with open(chemin, "rb") as fichier:
        limites = tomllib.load(fichier)
    limites["dossier_fiches"] = RACINE / limites["dossier_fiches"]
    return limites


def charger_configuration():
    """Lit .env et renvoie la configuration du service d’IA dans un dictionnaire."""
    load_dotenv(RACINE / ".env")
    service = os.getenv("SERVICE", "litellm")
    if service == "simule":
        return {"service": "simule", "modele": "simule"}
    # À faire (étape 1) : lire LITELLM_API_KEY, LITELLM_BASE_URL et MODELE ;
    # lever ConfigurationInvalide avec un message qui dit quoi faire si la clé ou l’adresse manque ;
    # renvoyer {"service": "litellm", "url": ..., "cle": ..., "modele": ...}.
    raise NotImplementedError("Étape 1 : charger_configuration")
