# AR - Demande Sortie Caisse

Module Odoo de gestion des demandes de sortie de caisse.

Le module gere les demandes de depense, les lignes de details, les pieces justificatives, les validations Manager N+1, Tresorerie, Finance, MD, puis les etapes de saisie et regularisation.

## Objectif fonctionnel

Centraliser les sorties de caisse et imposer un circuit de validation adapte au montant, au budget et au type de demande.

Le module permet de :

- creer une demande de sortie de caisse ;
- categoriser le type de demande ;
- ajouter des lignes de depense ;
- calculer automatiquement le total demande ;
- appliquer une regle de validation ;
- verifier le budget mensuel ;
- valider par Manager N+1, Tresorerie, FI et MD selon le cas ;
- saisir les montants donnes et depenses ;
- calculer le montant a rendre ;
- regulariser la demande ;
- imprimer un rapport ;
- notifier les acteurs par email ;
- tracer les validations et refus dans le chatter.

## Roles fonctionnels

### Demandeur

Le demandeur initie la demande.

Il peut :

- creer la demande ;
- choisir le type de demande ;
- renseigner la description ;
- ajouter les lignes de depense ;
- joindre les justificatifs ;
- soumettre la demande ;
- recevoir les notifications d'acceptation, refus ou demande de modification.

### Manager N+1

Le Manager N+1 valide la pertinence du besoin.

Condition importante : l'utilisateur doit etre le Manager N+1 reel du demandeur.

### Tresorerie

La Tresorerie intervient selon la regle de validation appliquee.

Elle peut :

- valider la disponibilite ou le traitement tresorerie ;
- renseigner les etapes de saisie ;
- suivre la regularisation.

### Finance

Finance valide la demande apres Tresorerie lorsque le workflow le requiert.

### MD

MD intervient lorsque le montant, le type de demande ou la regle de validation impose une validation direction.

### Administrateur

L'administrateur gere les budgets, les regles de validation, les droits et la documentation.

## Types de demande

Les types principaux sont :

- cas d'urgence ;
- repas ;
- moyens generaux ;
- envoi postal ;
- indemnite RH ;
- maintenance ;
- autre.

Lorsque le type `Autre` est choisi, le champ de precision doit etre renseigne.

## Etats du workflow

Les etats principaux sont :

- `Expression de besoin`
- `Validation N+1`
- `Tresorerie`
- `Validation FI`
- `Validation MD`
- `Saisie`
- `Regularisation`
- `Archive`
- `Refusee`

## Flux standard

1. `Expression de besoin`
2. `Validation N+1`
3. `Tresorerie`
4. `Validation FI`
5. `Validation MD` si requis
6. `Saisie`
7. `Regularisation`
8. `Archive`

Les etapes exactes dependent de la regle de validation et du budget.

## Saisie et regularisation

L'etape de saisie permet de renseigner :

- montant donne ;
- montant depense ;
- justificatifs de saisie.

Le montant a rendre est calcule automatiquement.

La regularisation cloture le traitement et archive la demande.

## Refus et modification

La demande peut etre refusee par un acteur habilite avec motif.

Le bouton de modification permet de retourner la demande au demandeur lorsque des informations doivent etre corrigees.

## Notifications

Les emails couvrent les transitions vers :

- Manager N+1 ;
- Tresorerie ;
- FI ;
- MD ;
- saisie ;
- regularisation ;
- acceptation ;
- refus ;
- retour demandeur pour modification.

Fichier principal :

- `data/mail_templates.xml`

## Rapports

Le module fournit un rapport de demande de sortie de caisse.

Fichier principal :

- `reports/demande_sortie_caisse_report.xml`

## Modeles principaux

- `ar.demande.sortie.caisse`
- `ar.demande.sortie.caisse.line`
- `ar.sortie.caisse.regle.validation`
- `ar.sortie.caisse.budget`
- `ar.demande.sortie.caisse.documentation`
- `ar.demande.sortie.caisse.action.wizard`

## Structure du module

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`
- `data/sequence.xml`
- `data/mail_templates.xml`
- `reports/demande_sortie_caisse_report.xml`
- `views/demande_sortie_caisse_views.xml`
- `views/regle_validation_views.xml`
- `views/budget_views.xml`
- `views/documentation_views.xml`
- `views/menus.xml`
- `wizard/demande_sortie_caisse_action_wizard.py`
- `models/demande_sortie_caisse.py`
- `models/regle_validation.py`
- `models/budget.py`
- `models/documentation.py`

## Installation

1. Copier le module dans le dossier addons Odoo.
2. Redemarrer le serveur Odoo si necessaire.
3. Mettre a jour la liste des applications.
4. Installer le module.
5. Configurer les groupes N+1, Tresorerie, FI et MD.
6. Creer les regles de validation.
7. Configurer les budgets si necessaire.
8. Tester une demande avec et sans validation MD.

## Maintenance fonctionnelle

Lorsqu'une regle de caisse change, verifier aussi :

- les regles de validation ;
- les budgets ;
- le champ `state` ;
- les boutons du formulaire ;
- les assistants de validation/refus ;
- les templates email ;
- le rapport ;
- ce README.
