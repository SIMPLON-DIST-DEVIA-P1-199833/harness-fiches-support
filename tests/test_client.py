import pytest

from assistant.client import creer_client, envoyer, ServiceIndisponible
from assistant.configuration import charger_configuration


def test_exception_openai_transformee(limites):
    configuration = charger_configuration()
    client = creer_client(configuration, limites)
    with pytest.raises(ServiceIndisponible, match=r".*STATUS error.*"):
        envoyer(client, configuration["modele"], [], None)
