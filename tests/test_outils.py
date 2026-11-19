import pytest

from assistant.outils import AccesRefuse, lire_fiche


def test_refuse_une_fiche_hors_du_dossier(limites, tmp_path):
    (tmp_path / ".env.md").write_text("LITELLM_API_KEY=secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)
