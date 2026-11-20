import pytest

from assistant import conversation, client
from assistant.service_simule import (
    ServiceSimule,
    texte,
    panne,
    delai_depasse,
    cle_refusee,
)


def refuser(nom):
    return False


def ignorer(texte):
    pass


# Réponse du modèle
def test_renvoie_la_reponse_du_modele(limites):
    attendu = "Bonjour, que puis-je faire ?"
    service = ServiceSimule([texte(attendu)])
    messages = conversation.nouvelle_conversation(limites)
    reponse = conversation.poser(
        "Hello", messages, service, "simule", limites, refuser, ignorer
    )
    assert reponse == attendu


# Historique
def test_garde_l_historique(limites):
    question_1 = "Hello"
    reponse_1 = "Bonjour, que puis-je faire ?"
    service = ServiceSimule([texte(reponse_1), texte("R2")])
    messages = conversation.nouvelle_conversation(limites)

    conversation.poser(
        question_1, messages, service, "simule", limites, refuser, ignorer
    )
    conversation.poser("Q2?", messages, service, "simule", limites, refuser, ignorer)

    contenus = [m["content"] for m in service.requetes[1]["messages"]]
    assert question_1 in contenus
    assert reponse_1 in contenus


# Pannes du service
@pytest.mark.parametrize(
    "erreur, mot",
    [
        (panne(), "LITELLM_BASE_URL"),
        (delai_depasse(), "réessayer"),
        (cle_refusee(), "LITELLM_API_KEY"),
    ],
)
def test_panne_leve_service_indisponible(limites, erreur, mot):
    service = ServiceSimule([erreur])
    messages = conversation.nouvelle_conversation(limites)
    with pytest.raises(client.ServiceIndisponible) as erreur_levee:
        conversation.poser(
            "erreur", messages, service, "simule", limites, refuser, ignorer
        )
    assert mot in str(erreur_levee.value)


# # MÉMO pour la partie "réponse du modèle":
# je dois appeler conversation.poser car c'est la fonction testée
# pour utiliser .poser je dois remplir ses paramètres avec des arguments
# question : je remplis le message du technicien
# messages : c'est une liste, j'appelle nouvelle_conversation() pour faire comme en vrai
# service : je dois utiliser le ServiceSimule qui "reçoit une liste de réponse" donc c'est une liste et j'appelle texte car c'est ce que j'attends
# modele : peu importe ce sera le simulé, j'écris ce que je veux
# refuser + ignorer : fausses fonctions exigées par .poser (refuser → False, ignorer → ne fait rien)
# l'argument dans nouvelle_conversation est "limites" (fichier conversation.py) -> défini par pytest d'après l'indice (fixture de tests/conftest.py)
# je dois comparer la réponse de .poser à ce que j'attends, donc j'enregistre la réponse de .poser dans "reponse" et je déclare "attendu" avec une phrase bateau
# je passe donc mon "attendu" à "texte" dans la liste de ServiceSimule
# j'utilise un assert pour comparer la reponse et l'attendu.


def test_joint_la_fiche_a_la_question(limites):
    texte = conversation.joindre_fiche("modifier-taux-tva.md", "Résume.", limites)
    assert "Résume." in texte
    assert "# Modifier le taux de TVA" in texte
