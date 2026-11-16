# Tamia

Ton petit agent de poche pour planifier ton budget du mois.

Tamia est une appli web de budget prévisionnel par enveloppes : on indique sa paye, on la répartit entre ses enveloppes (épargne, loyer, abonnements…), on associe chaque enveloppe à une banque, puis on valide le mois.

## Fichiers

- `index.html` : page d'accueil
- `app.html` : l'application (connexion Firebase, budgets, rapports, réglages)
- `mentions-legales.html`, `confidentialite.html` : pages légales
- `firestore.rules` : règles de sécurité Firestore (à coller dans la console Firebase)
- `site.css`, `icon.svg`, `icon-*.png`, `manifest.webmanifest` : styles et icônes

## Hébergement

Site statique publié avec GitHub Pages (branche `main`, dossier racine). Données et comptes : Firebase Authentication + Cloud Firestore (projet `tamia-fe68f`).

