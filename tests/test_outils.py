import pytest

from assistant.outils import DEFINITIONS, AccesRefuse, lire_fiche, noms_fonctions


def test_refuse_une_fiche_hors_du_dossier(limites, tmp_path):
    (tmp_path / ".env.md").write_text("LITELLM_API_KEY=secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)


def test_noms_fonctions():
    result = noms_fonctions(DEFINITIONS)
    assert type(result) is list
    assert len(result) > 0 and type(result[0]) is str
