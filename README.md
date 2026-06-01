# AR - Demande Sortie Caisse


> Documentation du workflow de demande de sortie de caisse.


## Vue d?ensemble

Le module g?re les demandes de sortie de caisse depuis l?expression du besoin jusqu?? l?acceptation ou le refus. Il automatise la r?f?rence, calcule les montants depuis les lignes, applique des r?gles de validation selon les montants et trace chaque validation dans le chatter.

## Utilisateurs concern?s

- Demandeur : cr?e la demande et ajoute les lignes de d?pense.
- Manager N+1 : contr?le le besoin et valide ou refuse.
- Tr?sorerie : v?rifie la faisabilit? de sortie de caisse.
- Finance : valide la conformit? financi?re.
- Direction MD : valide les demandes n?cessitant un niveau sup?rieur.
- Administrateur : configure les r?gles de validation.

## Workflow m?tier

1. Expression de besoin
2. Validation N+1
3. Tr?sorerie
4. Validation FI
5. Validation MD si applicable
6. Accept?e
7. Refus?e avec motif

## Fonctionnement op?rationnel

- Le demandeur cr?e une demande et renseigne la description.
- Il ajoute les lignes de d?pense et pi?ces jointes.
- Il soumet la demande au manager N+1.
- Chaque validateur utilise le bouton correspondant ? son ?tape.
- En cas de refus, le motif est enregistr?.
- Une demande accept?e conserve les dates et utilisateurs de validation.

## Configuration recommand?e

- Cr?er au moins une r?gle de validation avec bornes de montant et validateurs.
- V?rifier les employ?s li?s aux utilisateurs afin de r?cup?rer manager et d?partement.
- Configurer les groupes et record rules.
- V?rifier les mod?les d?e-mail et la s?quence.

## D?pendances Odoo

- `base`
- `mail`
- `hr`

## Mod?les techniques

- `ar.demande.sortie.caisse` : Demande Sortie Caisse (`models/demande_sortie_caisse.py`)
- `ar.demande.sortie.caisse.line` : Ligne demande sortie caisse (`models/demande_sortie_caisse.py`)
- `ar.demande.sortie.caisse.documentation` : Sortie caisse - Documentation (`models/documentation.py`)
- `ar.sortie.caisse.regle.validation` : Règle de validation sortie caisse (`models/regle_validation.py`)
- `ar.demande.sortie.caisse.action.wizard` : Confirmation action demande sortie caisse (`wizard/demande_sortie_caisse_action_wizard.py`)

## ?tats d?tect?s dans le code

- `models/demande_sortie_caisse.py` : `expression_besoin` (Expression de besoin), `validation_n1` (Validation N+1), `tresorerie` (Trésorerie), `validation_fi` (Validation FI), `validation_md` (Validation MD), `acceptee` (Acceptée), `refusee` (Refusée)

## Actions serveur principales

- `action_soumettre` (`models/demande_sortie_caisse.py`)
- `action_valider_n1` (`models/demande_sortie_caisse.py`)
- `action_valider_tresorerie` (`models/demande_sortie_caisse.py`)
- `action_valider_fi` (`models/demande_sortie_caisse.py`)
- `action_valider_md` (`models/demande_sortie_caisse.py`)
- `action_refuser` (`models/demande_sortie_caisse.py`)
- `action_demander_modification` (`models/demande_sortie_caisse.py`)
- `action_open_modify_wizard` (`models/demande_sortie_caisse.py`)
- `action_open_validate_n1_wizard` (`models/demande_sortie_caisse.py`)
- `action_open_validate_tresorerie_wizard` (`models/demande_sortie_caisse.py`)
- `action_open_validate_fi_wizard` (`models/demande_sortie_caisse.py`)
- `action_open_validate_md_wizard` (`models/demande_sortie_caisse.py`)
- `action_open_refuse_wizard` (`models/demande_sortie_caisse.py`)
- `action_confirm` (`wizard/demande_sortie_caisse_action_wizard.py`)

## Fichiers charg?s par le manifest

- `data/sequence.xml`
- `data/mail_templates.xml`
- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`
- `views/demande_sortie_caisse_views.xml`
- `views/regle_validation_views.xml`
- `views/documentation_views.xml`
- `views/menus.xml`

## S?curit? et droits

Le module s?appuie sur les fichiers suivants pour d?finir les groupes, r?gles d?enregistrement et droits d?acc?s :

- `security/ir.model.access.csv`
- `security/record_rules.xml`
- `security/security.xml`

## Assets et interface

- `static/src/js/sortie_caisse_animations.js`
- `static/src/scss/ar_demande_sortie_caisse.scss`

## Bonnes pratiques d?utilisation

- V?rifier que chaque utilisateur Odoo est li? au bon employ? lorsque le module d?pend de `hr.employee`.
- Tester le workflow avec un dossier de test avant utilisation en production.
- Contr?ler les groupes de s?curit? apr?s installation afin que seuls les bons r?les voient les boutons de validation.
- Garder les templates e-mail et rapports align?s avec les proc?dures internes.
- Sauvegarder la base avant toute modification structurelle du module.

## Maintenance

- Les ?volutions fonctionnelles doivent ?tre ajout?es dans les mod?les Python, les vues XML et les r?gles de s?curit? correspondantes.
- Apr?s modification des vues, mettre ? jour le module depuis Odoo ou red?marrer le serveur selon le type de changement.
- Apr?s modification des assets, vider le cache navigateur et recompiler les assets si n?cessaire.
- Toute nouvelle ?tape de workflow doit ?tre accompagn?e des droits, boutons, notifications et filtres correspondants.
