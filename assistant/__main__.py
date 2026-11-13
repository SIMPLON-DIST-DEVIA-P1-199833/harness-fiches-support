"""Point d’entrée : python -m assistant, ou python -m assistant --verifier."""

import sys

from assistant.interface import lancer

sys.exit(lancer(verifier="--verifier" in sys.argv[1:]))
