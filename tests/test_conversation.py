import pytest

from assistant import client, conversation
from assistant.service_simule import ServiceSimule, cle_refusee, delai_depasse, panne, texte


def refuser(nom):
    return False


def ignorer(texte):
    pass


def test_renvoie_la_reponse_du_modele(limites):
    service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])
    messages = conversation.nouvelle_conversation(limites)
    reponse = conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)
    assert reponse == "Bonjour, que puis-je faire ?"


def test_garde_l_historique(limites):
    service = ServiceSimule([texte("Première réponse."), texte("Deuxième réponse.")])
    messages = conversation.nouvelle_conversation(limites)
    conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)
    conversation.poser("Et ensuite ?", messages, service, "simule", limites, refuser, ignorer)
    contenus = [message["content"] for message in service.requetes[1]["messages"]]
    assert "Bonjour" in contenus
    assert "Première réponse." in contenus


def test_une_panne_leve_service_indisponible(limites):
    service = ServiceSimule([panne()])
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(client.ServiceIndisponible):
        conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)


def test_un_delai_depasse_leve_service_indisponible(limites):
    service = ServiceSimule([delai_depasse()])
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(client.ServiceIndisponible):
        conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)


def test_une_cle_refusee_leve_service_indisponible(limites):
    service = ServiceSimule([cle_refusee()])
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(client.ServiceIndisponible):
        conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)


# Variante : les trois tests ci-dessus en un seul, lancé une fois par panne.
@pytest.mark.parametrize("erreur", [panne(), delai_depasse(), cle_refusee()])
def test_chaque_panne_leve_service_indisponible(limites, erreur):
    service = ServiceSimule([erreur])
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(client.ServiceIndisponible):
        conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)


# Pour aller plus loin : chaque couple (panne, mot attendu dans le message) donne un test.
@pytest.mark.parametrize(
    ("erreur", "consigne"),
    [(panne(), "LITELLM_BASE_URL"), (delai_depasse(), "renvoyer"), (cle_refusee(), "LITELLM_API_KEY")],
)
def test_le_message_de_panne_dit_quoi_faire(limites, erreur, consigne):
    service = ServiceSimule([erreur])
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(client.ServiceIndisponible) as erreur_levee:
        conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)
    assert consigne in str(erreur_levee.value)
