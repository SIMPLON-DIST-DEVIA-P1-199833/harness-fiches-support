import pytest
from assistant.service_simule import ServiceSimule, texte, panne, delai_depasse, cle_refusee
from assistant import conversation
from assistant import client


def refuser(nom):
    return False


def ignorer(texte):
    pass


def test_renvoie_la_reponse_du_modele(limites) :
    # Init service
    service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])
    # Poser question
    messages = conversation.nouvelle_conversation(limites)
    reponse = conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)
    assert reponse == "Bonjour, que puis-je faire ?"


def test_garde_l_historique(limites):
    service = ServiceSimule([texte("Bonjour, que puis-je faire ?"), texte("Comment je peux t'aider?")])
    messages = conversation.nouvelle_conversation(limites)
    reponse1 = conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)
    reponse2 = conversation.poser("Merci", messages, service, "simule", limites, refuser, ignorer)
    contenus = [m["content"] for m in service.requetes[1]["messages"]]
    assert "Bonjour" in contenus 
    assert reponse1 in contenus




@pytest.mark.parametrize("erreur", [panne(), delai_depasse(), cle_refusee()])
def test_une_panne_leve_service_indisponible(limites, erreur):
    service = ServiceSimule([erreur])
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(client.ServiceIndisponible):
        conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)