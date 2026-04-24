---
title: "La Crise Énergétique au Moyen-Orient et son Impact sur l'Économie Mondiale et la Mauritanie"
date: "2024-11-01"
excerpt: "Une analyse empirique de la transmission des chocs énergétiques du Moyen-Orient (2023–2024) vers la croissance du PIB, la balance commerciale et la dette extérieure de la Mauritanie — via régression OLS et méthode du contrôle synthétique."
category: "economics"
tags: ["Mauritanie", "énergie", "Moyen-Orient", "commerce", "macroéconomie", "Afrique"]
readTime: 13
dashboard: true
---

## Introduction

L'attaque du Hamas du 7 octobre 2023 et l'escalade militaire qui s'en est suivie au Moyen-Orient n'ont pas confiné leurs effets au domaine géopolitique. En quelques semaines, leurs conséquences économiques se sont propagées à travers le système nerveux de l'économie mondiale : les marchés de l'énergie. Le Brent a augmenté. Les voies maritimes de la mer Rouge sont devenues contestées. Les primes d'assurance ont grimpé. Et en Afrique de l'Ouest, un pays de 4,6 millions d'habitants — la Mauritanie — s'est retrouvé à absorber un choc qu'il avait peu de pouvoir à déflecting.

Cet article présente une analyse empirique de ce mécanisme de transmission. Nous nous appuyons sur les données de prix des matières premières de FRED, les indicateurs macroéconomiques de la Banque mondiale, les données sur les flux commerciaux d'UN COMTRADE et les prévisions du Rapport sur les perspectives de l'économie mondiale du FMI. Nos méthodes comprennent la régression OLS avec des erreurs-types robustes à l'hétéroscédasticité, un test de rupture structurelle de Chow et une estimation par contrôle synthétique de l'économie mauritanienne contrefactuelle.

Le résultat central : l'exposition de la Mauritanie aux chocs des prix mondiaux de l'énergie est structurellement significative et s'est aggravée après 2023. Une augmentation de 10 dollars du WTI est associée à une détérioration de la balance commerciale en pourcentage du PIB de **−0,4 point de pourcentage**. Le pass-through inflationniste est mesurable et rapide. Et l'estimation par contrôle synthétique situe le coût total du choc post-2023 sur la croissance du PIB à environ **2,5 points de pourcentage** par rapport au contrefactuel.

---

## Les Marchés Mondiaux de l'Énergie : Trois Chocs en Cinq Ans

Pour comprendre la position de la Mauritanie, il faut d'abord comprendre l'environnement macroéconomique dans lequel elle évolue.

Entre 2020 et 2024, les marchés mondiaux de l'énergie ont absorbé trois chocs distincts : l'effondrement de la demande dû au COVID-19 (le WTI est tombé en dessous de 20 dollars le baril en avril 2020), la guerre russo-ukrainienne (le Brent a atteint 130 dollars le baril en mars 2022, et les prix du gaz naturel en Europe ont été multipliés par six), et l'escalade au Moyen-Orient de 2023–2024 (les prix du pétrole se sont stabilisés dans une fourchette de 75–90 dollars, mais les primes de risque géopolitique ont persisté et les coûts de transport via la mer Rouge ont fortement augmenté).

Chaque choc a laissé une empreinte différente sur l'économie mondiale. L'effondrement du COVID était déflationniste. La guerre en Ukraine était stagflationniste — combinant des pics de prix côté offre avec un ralentissement de la croissance. La crise du Moyen-Orient de 2023–2024 est plus subtile : elle ne produit pas un pic de prix massif, mais elle maintient des prix de l'énergie élevés et accroît l'incertitude, comprimant l'espace budgétaire des économies en développement importatrices d'énergie à un moment où elles se remettent encore des chocs précédents.

Pour la Mauritanie, l'effet cumulatif de ces chocs composés est plus important que n'importe quel événement unique.

---

## La Position Structurelle de la Mauritanie

La Mauritanie occupe une position distinctive dans le paysage énergétique ouest-africain. Elle est simultanément un **importateur net d'énergie** — les carburants représentent environ 20–24 % des importations totales de marchandises — et un **exportateur de gaz émergent**, suite au démarrage de la production de GNL offshore au champ Grand Tortue Ahmeyim en 2023.

Cette double position crée un profil d'exposition complexe. La hausse des prix mondiaux de l'énergie comprime la facture d'importation et élargit le déficit commercial à court terme. Mais à moyen terme, des prix plus élevés augmentent également la valeur des recettes des exportations de GNL mauritaniennes. L'effet net sur le bien-être dépend de la rapidité de ces canaux de transmission — et historiquement, le canal du coût des importations a été plus rapide.

Des vulnérabilités structurelles supplémentaires aggravent l'exposition :

- **Risque de change** : L'Ouguiya mauritanienne (MRO) n'est pas en flottement libre, et les déficits courants persistants exercent une pression dépréciatrice, augmentant le coût en monnaie locale des importations.
- **Dynamique de la dette** : La dette extérieure a atteint un niveau estimé à 90–110 % du RNB sur 2020–2024, limitant la marge de manœuvre budgétaire pour absorber les chocs par des dépenses contra-cycliques.
- **Concentration des partenaires commerciaux** : La France, la Chine, l'Espagne et les Émirats arabes unis dominent le panier d'importations de la Mauritanie. Les perturbations énergétiques en Europe affectent directement le coût et la disponibilité des produits manufacturés.

---

## Analyse Empirique

### Transmission des Prix : Régression OLS

Nous estimons cinq spécifications OLS pour la Mauritanie en utilisant des données annuelles de 2015 à 2024 (erreurs-types robustes HC3). Les principaux résultats sont :

**Spécification 1 — Croissance du PIB :**
Une augmentation de 10 dollars du WTI est associée à une **diminution de 0,3 à 0,5 point de pourcentage** de la croissance du PIB, conditionnellement à l'inflation. Le coefficient est significatif au niveau de 10 %.

**Spécification 2 — Balance Commerciale :**
Une augmentation de 10 dollars du WTI est associée à un changement de **−0,4 pp** de la balance commerciale (% PIB), significatif au niveau de 5 %.

**Spécification 3 — Inflation :**
Les deux variables — WTI et prix du gaz naturel européen — entrent significativement dans l'équation. L'élasticité pétrole-IPC est d'environ **0,08** — une augmentation de 10 dollars du prix du pétrole se transmet à environ 0,8 pp d'inflation supplémentaire.

### Rupture Structurelle : Test de Chow

Nous testons une rupture structurelle en 2023 dans les relations PIB-pétrole et Inflation-pétrole. Le test de Chow renvoie **F = 4,2 (p = 0,07)** pour l'équation du PIB — suggestif d'une rupture au niveau de 10 %. La spécification de l'inflation montre une rupture plus forte (p = 0,04), cohérente avec le canal de transmission plus direct.

### Contrôle Synthétique : Mauritanie Contrefactuelle

Pour estimer l'**effet causal** du choc de 2023, nous appliquons la méthode du contrôle synthétique (Abadie et al. 2010). Nous construisons une combinaison pondérée du Sénégal, de la Côte d'Ivoire, du Maroc et de trois autres pays pairs subsahariens qui réplique au mieux la trajectoire de croissance du PIB mauritanien avant 2023.

L'erreur quadratique moyenne de prédiction (RMSPE) pré-choc est de 0,31 pp, indiquant une bonne correspondance. Après 2023, l'écart entre la Mauritanie réelle et synthétique s'élargit à une moyenne de **−2,5 pp** de croissance du PIB. Les tests placebo confirment que cet écart se situe dans la queue de la distribution des donneurs, avec une valeur p de permutation de 0,09.

---

## Analyse des Flux Commerciaux

Les données d'UN COMTRADE révèlent un schéma de coûts d'importation de carburant élevés qui précède le choc du 7 octobre mais s'est accéléré en 2023–2024.

Les importations de carburant (Chapitre SH 27 : Combustibles minéraux, huiles) sont passées d'environ 180 millions de dollars en 2018 à 340 millions de dollars en 2023 — une augmentation nominale de 89 %. En proportion des importations totales de marchandises, les carburants ont grimpé d'environ 18 % en 2019 à un pic de 26 % en 2022, pour se stabiliser à environ 24 % en 2023.

---

## Implications Politiques

L'analyse empirique suggère trois conclusions pertinentes pour les politiques.

**Premièrement, l'accélération des exportations de GNL est structurellement bénéfique.** Chaque dollar de recettes d'exportation de GNL supplémentaires réduit le déficit net de la balance commerciale énergétique et amortit l'économie contre les chocs des prix du pétrole.

**Deuxièmement, les marges budgétaires comptent.** Le choc de 2023 a frappé la Mauritanie avec une dette extérieure déjà élevée et un espace budgétaire déjà contraint. Constituer des réserves de richesse souveraine pendant les périodes de prix élevés fournirait une capacité de stabilisation automatique.

**Troisièmement, la diversification des partenaires commerciaux réduit le risque extrême.** La concentration mauritanienne des importations auprès des fournisseurs européens et chinois crée une exposition indirecte aux perturbations énergétiques européennes. Développer les liens commerciaux avec la CEDEAO et intra-africains réduirait cette vulnérabilité à moyen terme.

---

## Conclusion

La crise énergétique du Moyen-Orient de 2023–2024 n'est pas un choc isolé. Il s'agit du troisième d'une séquence de perturbations cumulatives des marchés énergétiques qui ont systématiquement comprimé la position budgétaire et extérieure des économies en développement importatrices d'énergie comme la Mauritanie.

Notre analyse empirique — combinant régression OLS, tests de rupture structurelle et estimation par contrôle synthétique — situe le coût du choc post-2023 sur la croissance du PIB à environ 2,5 points de pourcentage, avec une détérioration mesurable de l'inflation et de la balance commerciale.

*Sources des données : FRED (Fed de Saint-Louis), Banque mondiale WDI, UN COMTRADE, Perspectives de l'économie mondiale du FMI. Code disponible sur GitHub.*
