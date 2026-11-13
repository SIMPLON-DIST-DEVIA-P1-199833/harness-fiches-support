import pytest

from assistant.configuration import charger_limites


@pytest.fixture
def limites(tmp_path):
    """Limites de l’équipe, avec un dossier de fiches temporaire contenant une fiche."""
    limites = charger_limites()
    dossier = tmp_path / "fiches"
    dossier.mkdir()
    (dossier / "modifier-taux-tva.md").write_text("# Modifier le taux de TVA\n", encoding="utf-8")
    limites["dossier_fiches"] = dossier
    return limites
