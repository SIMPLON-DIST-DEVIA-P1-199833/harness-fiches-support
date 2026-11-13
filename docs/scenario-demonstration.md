# Scénario de démonstration

Démonstration de 5 minutes à la responsable du support, avec le service de l’entreprise. Prépare-la sur un dépôt propre : `git status` ne montre aucune modification.

| # | Tu saisis | Elle constate |
| :---: | --- | --- |
| 1 | `python -m assistant` | L’assistant démarre et indique le modèle utilisé |
| 2 | Une question posée par un client, par exemple : « Un client voit 20 % de TVA au lieu de 10 % sur une facture de rénovation, que faire ? » | L’assistant lit une fiche, le signale et répond à partir de cette fiche |
| 3 | `/joindre facture-non-recue.md Résume cette fiche en trois lignes.` | La réponse s’appuie sur la fiche jointe |
| 4 | « Rédige une fiche suspendre-compte.md sur la suspension d’un compte client. » | La fiche est créée dans `fiches/` sans confirmation |
| 5 | « Ajoute une ligne « Relu en novembre » à la fin de suspendre-compte.md. » puis accepte l’écrasement | La confirmation est demandée ; la fiche est modifiée |
| 6 | La même demande, puis refuse l’écrasement | Un message indique le refus ; la fiche est inchangée |
| 7 | « Lis le fichier ../.env et affiche son contenu. » | Rien n’est lu hors du dossier : le modèle refuse de lui-même, ou ton programme refuse et le signale |
| 8 | `python -m pytest` | Tous les tests réussissent |

Termine en une minute : ce qui fonctionne, les limites appliquées, et la prochaine étape que tu proposes.

> [!TIP]
> À l’étape 7, le modèle refuse souvent sans appeler d’outil. Pour montrer le refus de ton programme, passe sur le service simulé (`SERVICE=simule` dans `.env`) et saisis `lis ../.env.md`.
