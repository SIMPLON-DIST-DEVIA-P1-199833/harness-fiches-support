import pytest
from assistant import conversation
from assistant.service_simule import ServiceSimule, texte, panne, delai_depasse, cle_refusee
from assistant.client import ServiceIndisponible
from assistant.outils import AccesRefuse

def refuser(nom):
    """Refuse tout écrasement de fiche."""
    return False


def ignorer(texte):
    """N'affiche rien (pas d'interface en test)."""
    pass


def test_renvoie_la_reponse_du_modele(limites):
    # Le service simulé renverra ce texte, puis s'arrêtera.
    service = ServiceSimule([texte("Hello world")])

    messages = conversation.nouvelle_conversation(limites)
    reponse = conversation.poser(
        "World", messages, service, "simule", limites, refuser, ignorer
    )
    assert reponse == "Hello world"

def test_garde_l_historique(limites):
    # /!\ Ce sont des tuples : couple 1-question 2- réponse du service simulé /!\
    echanges = [
        ("Bonjour", "Réponse à la première question"),
        ("Et la suite ?", "Réponse à la deuxième question"),
        ("Encore une ?", "Réponse à la troisième question"),
    ]
    # --- ÉTAPE 1 : préparer ce que le service simulé va renvoyer ---
    # "reponse" ici = le texte simulé prévu (ex. "Réponse à la première question").
    # On l'enveloppe dans texte(...) pour que ServiceSimule le renvoie tel quel.
    # Résultat : reponses_simulees = [texte("..."), texte("..."), texte("...")]
    # Init liste vide
    reponses_simulees = []
    # Pour chaque échange, la réponse donnée...
    for question, reponse in echanges:
        #accrocher la réponse donnée dans la liste réponse simulée
        reponses_simulees.append(texte(reponse))
    #Création du service pour démarrer une convo et traquer les messages
    service = ServiceSimule(reponses_simulees)
    messages = conversation.nouvelle_conversation(limites)

    # --- ÉTAPE 2 : poser les questions et récupérer les réponses réelles ---
    # "reponse" ici = la valeur renvoyée par poser (ce que le service a effectivement renvoyé).
    # On la stocke dans la liste "reponses" pour la comparer ensuite.
    # Poser toutes les questions, stocker les réponses
    reponses = []
    for question, reponse in echanges:
        reponse = conversation.poser(
            question, messages, service, "simule", limites, refuser, ignorer
        )
        reponses.append(reponse)
    # --- ÉTAPE 3 : vérifier que l'historique grandit ---
    # À chaque appel, poser ajoute la question + la réponse à "messages".
    # Donc le 2ᵉ appel reçoit plus de messages que le 1ᵉʳ, etc.
    for i in range(1, len(service.requetes)):
        assert len(service.requetes[i]["messages"]) > len(service.requetes[i - 1]["messages"])
    # --- ÉTAPE 4 : vérifier que chaque question est présente dans le dernier appel ---
    # On extrait le contenu textuel de chaque message du dernier appel.
    # 2. Chaque question est présente dans le dernier appel
    dernier_appel = service.requetes[-1]["messages"]
    contenus = []
    for message in dernier_appel:
        contenus.append(message.get("content", "") or "")
    for question, reponse in echanges:
        assert any(question in c for c in contenus), f"Question absente : {question}"

    # --- ÉTAPE 5 : comparer réponse réelle vs réponse attendue ---
    # reponses[i]       = ce que poser a renvoyé (réponse réelle)
    # reponse_attendue  = le 2ᵉ élément du tuple (réponse simulée attendue)
    # 3. Les réponses sont bien celles attendues, dans l'ordre
    i = 0
    for question, reponse_attendue in echanges:
        assert reponses[i] == reponse_attendue
        i = i + 1

def test_injoignable(limites):
    service = ServiceSimule([panne()])
    messages = conversation.nouvelle_conversation(limites)

    with pytest.raises(ServiceIndisponible):
        conversation.poser(
            "panne", messages, service, "simule", limites, refuser, ignorer
        )

def test_non_authentifie(limites):
    service = ServiceSimule([cle_refusee()])
    messages = conversation.nouvelle_conversation(limites)

    with pytest.raises(ServiceIndisponible):
        conversation.poser(
            "refus", messages, service, "simule", limites, refuser, ignorer
        )

def test_timeout(limites):
    service = ServiceSimule([delai_depasse()])
    messages = conversation.nouvelle_conversation(limites)

    with pytest.raises(ServiceIndisponible):
        conversation.poser(
            "lent", messages, service, "simule", limites, refuser, ignorer
        )

def test_injoignable_message(limites):
    service = ServiceSimule([panne()])
    messages = conversation.nouvelle_conversation(limites)

    with pytest.raises(ServiceIndisponible) as erreur:
        conversation.poser(
            "panne", messages, service, "simule", limites, refuser, ignorer
        )
    assert "Service IA injoignable, problème de connexion" in str(erreur.value)

def test_cle_api_message(limites):
    service = ServiceSimule([cle_refusee()])
    messages = conversation.nouvelle_conversation(limites)

    with pytest.raises(ServiceIndisponible) as erreur:
        conversation.poser(
            "panne", messages, service, "simule", limites, refuser, ignorer
        )
    assert "Erreur d'authentification clé API" in str(erreur.value)

def test_timeout_message(limites):
    service = ServiceSimule([delai_depasse()])
    messages = conversation.nouvelle_conversation(limites)

    with pytest.raises(ServiceIndisponible) as erreur:
        conversation.poser(
            "panne", messages, service, "simule", limites, refuser, ignorer
        )
    assert "Erreur délai dépassé" in str(erreur.value)