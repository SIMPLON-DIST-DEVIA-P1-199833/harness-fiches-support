## Ton assistant


### Installation

j'ai crée un environnement virtuel python pour isoler les dépendances du projet avec python -m venv .venv

puis j'ai installé les dépendances du projet à partir du fichier requirements.txt.
et tapé dans le terminale ./.venv/Scripts/python.exe -m pip install -r requirements.txt

### Configuration

j'ai crée le fichier .env à partir du fichier .env.example pour configurer le service d'iA avec cp .env.example.env

dans le fichier env j'ai renseigné ma clé personnelle et utilisé l'adresse du service déjà fournie
le fichier .env est ignoré par Git pour éviter de publier ma clé sur Github

### Vérification de l'accès

Pour vérifier que mon assistant communique le service d'Ia j'ai exécuté la commande ./.venv/Scripts/python.exe -m assistant --verifier

un message " accès verifié " s'affiche dans le terminal ce qui confirme que la connexion fonctionne
> À compléter au fil des étapes : installation, configuration
> de la clé (sans sa valeur), lancement, comportement aux
> limites, et comparaison de l’étape 3.