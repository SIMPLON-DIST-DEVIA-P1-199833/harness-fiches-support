import pytest
from pathlib import Path
from assistant.outils import AccesRefuse, lire_fiche, ecrire_fiche


def test_refuse_une_fiche_hors_du_dossier(limites, tmp_path):
    (tmp_path / ".env.md").write_text("LITELLM_API_KEY=secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)

def test_lit_une_fiche_du_dossier(limites):
    assert lire_fiche("modifier-taux-tva.md", limites) == "# Modifier le taux de TVA\n"

def test_refuse_un_chemin_absolu(limites):
    # / <- Pathlib operateur pour créer des chemins  
    chemin_absolu = str(Path("C:/") / "hors-du-dossier.md")
    with pytest.raises(AccesRefuse):
        lire_fiche(chemin_absolu, limites)