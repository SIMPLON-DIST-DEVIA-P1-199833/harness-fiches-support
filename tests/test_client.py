import pytest

from assistant.client import ServiceIndisponible, creer_client, envoyer
from assistant.configuration import charger_configuration


def test_exception_openai_transformee(limites):
    configuration = charger_configuration()
    client = creer_client(configuration, limites)
    with pytest.raises(ServiceIndisponible, match=r".*STATUS error.*"):
        envoyer(client, configuration["modele"], [], None)
