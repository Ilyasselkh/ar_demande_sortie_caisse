# AR - Demande Sortie Caisse

Module Odoo de gestion des demandes de sortie de caisse avec lignes de depense, pieces jointes, regles de validation par montant et validations N+1, tresorerie, finance et direction.

## Objectif

Cette documentation explique le perimetre fonctionnel du module, les roles utilisateurs, le workflow, la configuration et les principaux objets techniques.

## Utilisateurs concernes

- Demandeur
- Manager N+1
- Tresorerie
- Finance
- Direction MD
- Administrateur Odoo

## Workflow metier

1. Expression de besoin
2. Validation N+1
3. Tresorerie
4. Validation FI
5. Validation MD si applicable
6. Acceptee
7. Refusee avec motif

## Fonctionnement operationnel

- Creer la demande et renseigner la description.
- Ajouter les lignes de depense.
- Joindre les justificatifs.
- Soumettre au manager.
- Valider chaque etape selon le role.
- Consulter dates, validateurs et motif de refus dans le chatter.

## Configuration recommandee

- Creer les regles de validation avec bornes de montant.
- Renseigner les validateurs tresorerie, FI et MD.
- Verifier les employes lies aux utilisateurs.
- Configurer groupes, record rules et templates mail.

## Dependances Odoo

- `base`
- `mail`
- `hr`

## Modeles principaux

- `ar.demande.sortie.caisse`
- `ar.demande.sortie.caisse.line`
- `ar.sortie.caisse.regle.validation`
- `ar.demande.sortie.caisse.documentation`
- `ar.demande.sortie.caisse.action.wizard`

## Structure importante du module

- `security/ir.model.access.csv`
- `security/record_rules.xml`
- `security/security.xml`
- `data/mail_templates.xml`
- `data/sequence.xml`
- `views/demande_sortie_caisse_views.xml`
- `views/documentation_views.xml`
- `views/menus.xml`
- `views/regle_validation_views.xml`
- `wizard/__init__.py`
- `wizard/demande_sortie_caisse_action_wizard.py`
- `models/__init__.py`
- `models/demande_sortie_caisse.py`
- `models/documentation.py`
- `models/regle_validation.py`

## Securite

Les droits sont geres par les fichiers du dossier `security`. Il faut verifier les groupes, les regles enregistrement et les acces CSV apres installation ou modification du module.

## Notifications et suivi

Les modules qui dependent de `mail` utilisent le chatter Odoo pour tracer les changements. Les templates mail presents dans le dossier `data` servent a notifier les acteurs concernes par les transitions.

## Installation

1. Copier le module dans le dossier addons Odoo.
2. Redemarrer le serveur Odoo si necessaire.
3. Mettre a jour la liste des applications.
4. Installer ou mettre a jour le module.
5. Verifier les droits utilisateurs et tester un dossier de bout en bout.

## Maintenance

- Ajouter toute nouvelle etape a la fois dans le modele Python, les vues XML, les droits et les notifications.
- Tester les workflows avec plusieurs roles utilisateurs.
- Mettre a jour les rapports et templates mail quand la procedure interne change.
- Eviter de modifier les donnees de production sans sauvegarde.
- Documenter toute evolution fonctionnelle dans ce README.
