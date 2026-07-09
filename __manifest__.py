{
    "name": "AR - Demande Sortie Caisse",
    "version": "1.0.0",
    "summary": "Gestion des demandes de sortie de caisse",
    "description": """
Module de gestion des demandes de sortie de caisse avec workflow :
- Expression de besoin
- Validation N+1
- Trésorerie
- Validation FI
- Validation MD
- Acceptée
- Refusée
    """,
    "author": "AR IT Department",
    "category": "Accounting",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
    ],
    "data": [
        "data/sequence.xml",
        "data/mail_templates.xml",
        "security/security.xml",
        "security/record_rules.xml",
        "security/ir.model.access.csv",
        "reports/demande_sortie_caisse_report.xml",
        "views/solde_caisse_views.xml",
        "views/demande_sortie_caisse_views.xml",
        "views/regle_validation_views.xml",
        "views/budget_views.xml",
        "views/documentation_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ar_demande_sortie_caisse/static/src/scss/ar_demande_sortie_caisse.scss",
            "ar_demande_sortie_caisse/static/src/js/sortie_caisse_animations.js",
            "ar_demande_sortie_caisse/static/src/js/caisse_search_panel_period.js",
        ],
    },
    "application": True,
    "installable": True,
}
