import pytest

from assistant.outils import AccesRefuse, lire_fiche


def test_refuse_une_fiche_hors_du_dossier(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)

def test_lit_une_fiche_du_dossier(limites):
    texte = lire_fiche("modifier-taux-tva.md", limites) 
    assert "# Modifier le taux de TVA" in texte

def test_refuse_un_chemin_absolu(limites):
    with pytest.raises(AccesRefuse):
        lire_fiche("/home/hossk/projets-dev-ia/harness-fiches-support/docs/atelier-pytest.md", limites)