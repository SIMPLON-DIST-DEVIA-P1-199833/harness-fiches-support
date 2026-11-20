import pytest

from assistant.conversation import lister_fiches


def test_lister_fiches(limites):
    result = lister_fiches(limites)
    assert type(result) is str and result.startswith(" - ") and "modifier-taux-tva.md" in result
