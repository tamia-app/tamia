# Destinations de voyage

`destinations.json` alimente l'onglet Voyages de tamia. Tous les montants sont en euros.

## Structure

- `schemaVersion` : version du format (1).
- `updatedAt` : date de la dernière mise à jour du fichier.
- `checkEveryMonths` : au-delà de ce délai, une destination doit être revérifiée (6 mois).
- `margin` : marge pour les imprévus ajoutée au total (0,10 = 10 %).
- `departures` : villes de départ, avec un coefficient appliqué au prix du vol depuis Paris (`factor`).
- `seasonNames` : libellés des saisons `low`, `mid`, `high`.
- `destinations` : une entrée par ville :
  - `id`, `name`, `country`, `countryCode`, `zone`, `coords` [longitude, latitude], `color`, `aliases` (mots acceptés dans la recherche) ;
  - `seasons` : la saison de chaque mois, de `"1"` (janvier) à `"12"` (décembre) ;
  - `flights` : vol aller-retour en classe éco depuis Paris, par personne, pour chaque saison (`low`, `mid`, `high`) ;
  - `lodging` : prix d'une nuit pour une chambre de 2, par style (`malin`, `confort`, `plaisir`) et par saison ;
  - `daily` : par jour et par personne, par style : `food` (repas), `transport` (transports sur place), `activities` (activités et visites) ;
  - `fees` : `cityTaxPerPersonNight` (taxe de séjour par personne et par nuit, par style), `perPerson` (formalités payées une fois, par exemple ESTA ou ETA) et `perPersonLabel` ;
  - `info` : `currency`, `language`, `formalities`, `plug`, `timeDiff`, `flightTime`, `bestMonths`, `tip` ;
  - `meta` : `updatedAt` (date de la dernière vérification des prix), `confidence`, `sources`.

## Calcul de l'estimation

- Vols : prix de la saison du mois de départ × coefficient de la ville de départ × voyageurs.
- Logement : nuits (jours − 1) × chambres (voyageurs ÷ 2, arrondi au-dessus) × prix de la nuit.
- Repas, transports, activités : jours × voyageurs × montant du style.
- Taxes : taxe de séjour × nuits × voyageurs, plus les formalités × voyageurs.
- Total : somme des postes + marge, affiché en fourchette de −8 % à +8 %.

## Check-up

```bash
python3 tools/check_destinations.py
```

Le script vérifie la structure, la cohérence des prix (un style plus haut coûte plus cher, la haute saison plus que la basse) et signale les destinations dont les prix datent de plus de `checkEveryMonths` mois. Il tourne automatiquement sur GitHub à chaque modification des données et le 1er de chaque mois : un échec signale une erreur ou des prix à revérifier.

Pour mettre à jour une destination : corriger les montants, changer `meta.updatedAt` à la date du jour, relancer le check-up.
