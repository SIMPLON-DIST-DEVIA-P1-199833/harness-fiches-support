import pytest

from assistant.outils import AccesRefuse, lire_fiche, chemin_autorise
from assistant.configuration import RACINE


def test_refuse_une_fiche_hors_du_dossier(limites, tmp_path):
    (tmp_path / ".env.md").write_text("LITELLM_API_KEY=secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)


def test_lit_une_fiche_du_dossier(limites):
    contenu = lire_fiche("modifier-taux-tva.md", limites)
    assert contenu == "# Modifier le taux de TVA\n"


def test_refuse_chemin_absolu(limites):
    hors_dossier = RACINE / "docs" / "organisation-du-code.md"
    with pytest.raises(AccesRefuse):
        chemin_autorise(str(hors_dossier), limites)
