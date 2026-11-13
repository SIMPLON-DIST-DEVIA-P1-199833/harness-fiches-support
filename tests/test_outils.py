import pytest

from assistant.outils import AccesRefuse, lire_fiche


def test_refuse_une_fiche_hors_du_dossier(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)
