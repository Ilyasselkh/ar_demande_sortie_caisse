# AR - Demande Sortie Caisse

Module Odoo de gestion des demandes de sortie de caisse avec workflow de validation multi-niveaux.

## Objectif

Ce module permet à un collaborateur de saisir une demande de sortie de caisse, d'ajouter les lignes de dépense et les pièces jointes, puis de faire valider la demande par les acteurs concernés : manager N+1, trésorerie, finance et direction.

## Dépendances

- `base`
- `mail`
- `hr`

## Modèles principaux

- `ar.demande.sortie.caisse` : entête de la demande.
- `ar.demande.sortie.caisse.line` : détails/lignes de dépense.
- `ar.sortie.caisse.regle.validation` : règles de validation selon les montants.
- `ar.demande.sortie.caisse.documentation` : documentation métier accessible depuis le module.
- `ar.demande.sortie.caisse.action.wizard` : assistant de confirmation des actions sensibles.

## Workflow

La demande suit les états suivants :

1. `expression_besoin` : création et saisie par le demandeur.
2. `validation_n1` : validation du manager N+1.
3. `tresorerie` : contrôle par la trésorerie.
4. `validation_fi` : validation finance.
5. `validation_md` : validation direction si la règle appliquée l'exige.
6. `acceptee` : demande validée.
7. `refusee` : demande refusée avec motif.

## Fonctionnement

- La référence est générée automatiquement par séquence.
- Le demandeur, le manager N+1 et le département sont déduits de l'employé lié à l'utilisateur.
- Le montant demandé est calculé depuis les lignes.
- Les validateurs trésorerie, FI et MD sont déterminés par les règles de validation.
- Les boutons visibles dépendent de l'état, du rôle de l'utilisateur et des droits calculés.
- Le chatter conserve les changements d'état, validations, dates, motifs et commentaires.

## Notifications et documents

Le module charge des modèles d'e-mails, des séquences et des vues de documentation. Les pièces jointes peuvent être ajoutées sur la demande.

## Sécurité

Les droits, groupes et règles d'enregistrement sont fournis dans :

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`

## Rapports et interface

Le module ajoute des vues métier, menus, styles SCSS et animations JavaScript pour améliorer la lecture du workflow.

