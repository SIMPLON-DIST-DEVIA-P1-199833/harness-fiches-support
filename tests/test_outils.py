import pytest

from assistant.outils import AccesRefuse, ecrire_fiche, lire_fiche


def test_refuse_une_fiche_hors_du_dossier(limites, tmp_path):
    (tmp_path / ".env.md").write_text("LITELLM_API_KEY=secret", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche("../.env.md", limites)

def test_lit_une_fiche_du_dossier(limites):
    texte = lire_fiche("modifier-taux-tva.md", limites) 
    assert "# Modifier le taux de TVA\n" in texte

def test_refuse_un_chemin_absolu(limites, tmp_path):
    hors_dossier = tmp_path / "secret.md"
    hors_dossier.write_text("# Secret\n", encoding="utf-8")
    with pytest.raises(AccesRefuse):
        lire_fiche(str(hors_dossier), limites)

def test_ecrire_fiche_creation_sans_confirmation(limites):
    def confirmer_interdit(nom):
        pytest.fail("Confirmer ne doit pas être appelé pour une création")
    resultat = ecrire_fiche("suspendre-compte.md", "# Suspendre un compte\n", limites, confirmer_interdit)
    fiche = limites["dossier_fiches"] / "suspendre-compte.md"
    assert fiche.read_text(encoding="utf-8") == "# Suspendre un compte\n"
    assert "suspendre-compte.md" in resultat

def test_ecrire_fiche_ecrasement_refuse(limites):
    fiche = limites["dossier_fiches"] / "modifier-taux-tva.md"
    original = fiche.read_text(encoding="utf-8")
    with pytest.raises(AccesRefuse):
        ecrire_fiche("modifier-taux-tva.md", "contenu remplacé", limites, lambda nom: False)
    assert fiche.read_text(encoding="utf-8") == original