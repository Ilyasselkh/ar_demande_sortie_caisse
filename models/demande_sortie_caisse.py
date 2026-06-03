from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError


class ARDemandeSortieCaisse(models.Model):
    _name = "ar.demande.sortie.caisse"
    _description = "Demande Sortie Caisse"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Référence",
        default="Nouveau",
        readonly=True,
        copy=False,
        tracking=True,
    )
    state = fields.Selection([
        ("expression_besoin", "Expression de besoin"),
        ("validation_n1", "Validation N+1"),
        ("validation_fi", "Validation FI"),
        ("tresorerie", "Trésorerie"),
        ("validation_md", "Validation MD"),
        ("saisie", "Saisie"),
        ("regularisation", "Régularisation"),
        ("acceptee", "Archive"),
        ("refusee", "Refusée"),
    ], string="État", default="expression_besoin", required=True, tracking=True)

    demandeur_id = fields.Many2one(
        "hr.employee",
        string="Demandeur",
        default=lambda self: self._default_employee(),
        readonly=True,
        tracking=True,
    )
    demandeur_user_id = fields.Many2one(
        "res.users",
        string="Utilisateur demandeur",
        compute="_compute_demandeur_user_id",
        store=True,
    )
    manager_n1_id = fields.Many2one(
        "hr.employee",
        string="Manager N+1",
        compute="_compute_manager_n1_id",
        store=True,
        readonly=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Département",
        compute="_compute_department_id",
        store=True,
        readonly=True,
        tracking=True,
    )
    date_demande = fields.Datetime(
        string="Date",
        default=fields.Datetime.now,
        readonly=True,
        tracking=True,
    )
    montant_demande = fields.Float(
        string="Montant demandé",
        compute="_compute_total_prix",
        store=True,
        readonly=True,
        tracking=True,
    )
    montant_demande_display = fields.Char(
        string="Montant demandé",
        compute="_compute_total_prix",
        readonly=True,
    )
    type_demande = fields.Selection([
        ("indemnite_rh", "Indemnité RH"),
        ("reception_boissons", "Réception/Boissons"),
        ("cas_urgence", "Cas d’urgence"),
        ("moyens_generaux", "Moyens généraux"),
        ("poste", "Poste"),
        ("maintenance", "Maintenance"),
        ("autre", "Autre"),
    ], string="Type de demande", required=True, tracking=True)
    type_demande_autre = fields.Char(string="Autre type de demande", tracking=True)
    description_demande = fields.Text(string="Description de la demande", required=True, tracking=True)
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "ar_sortie_caisse_attachment_rel",
        "demande_id",
        "attachment_id",
        string="Pièces jointes",
        tracking=True,
    )
    line_ids = fields.One2many(
        "ar.demande.sortie.caisse.line",
        "demande_id",
        string="Détails de la demande",
        tracking=True,
    )
    total_prix = fields.Float(
        string="Total des prix",
        compute="_compute_total_prix",
        store=True,
        tracking=True,
    )
    total_prix_display = fields.Char(
        string="Total des prix",
        compute="_compute_total_prix",
        readonly=True,
    )
    montant_depense = fields.Float(string="Montant dépensé", tracking=True)
    montant_depense_display = fields.Char(
        string="Montant dépensé",
        compute="_compute_montants_saisie",
        readonly=True,
    )
    montant_a_rendre = fields.Float(
        string="Montant à rendre",
        compute="_compute_montants_saisie",
        store=True,
        readonly=True,
        tracking=True,
    )
    montant_a_rendre_display = fields.Char(
        string="Montant à rendre",
        compute="_compute_montants_saisie",
        readonly=True,
    )
    justificatif_saisie_ids = fields.Many2many(
        "ir.attachment",
        "ar_sortie_caisse_saisie_attachment_rel",
        "demande_id",
        "attachment_id",
        string="Justificatifs de saisie",
        tracking=True,
    )

    regle_validation_id = fields.Many2one(
        "ar.sortie.caisse.regle.validation",
        string="Règle de validation",
        readonly=True,
        tracking=True,
    )
    tresorier_id = fields.Many2one("res.users", string="Trésorerie", readonly=True, tracking=True)
    validateur_fi_id = fields.Many2one("res.users", string="Validation FI", readonly=True, tracking=True)
    validateur_md_prevu_id = fields.Many2one("res.users", string="Validation MD prévue", readonly=True, tracking=True)

    date_validation_n1 = fields.Datetime(string="Date validation N+1", readonly=True, tracking=True)
    date_validation_tresorerie = fields.Datetime(string="Date validation Trésorerie", readonly=True, tracking=True)
    date_validation_fi = fields.Datetime(string="Date validation FI", readonly=True, tracking=True)
    date_validation_md = fields.Datetime(string="Date validation MD", readonly=True, tracking=True)
    date_saisie = fields.Datetime(string="Date de saisie", readonly=True, tracking=True)
    date_regularisation = fields.Datetime(string="Date régularisation", readonly=True, tracking=True)
    date_acceptation = fields.Datetime(string="Date d'archive", readonly=True, tracking=True)
    date_refus = fields.Datetime(string="Date de refus", readonly=True, tracking=True)
    validateur_n1_id = fields.Many2one("res.users", string="Validé par N+1", readonly=True, tracking=True)
    validateur_tresorerie_id = fields.Many2one("res.users", string="Validé par Trésorerie", readonly=True, tracking=True)
    validateur_fi_done_id = fields.Many2one("res.users", string="Validé par FI", readonly=True, tracking=True)
    validateur_md_id = fields.Many2one("res.users", string="Validé par MD", readonly=True, tracking=True)
    saisie_user_id = fields.Many2one("res.users", string="Saisie par", readonly=True, tracking=True)
    regularisateur_id = fields.Many2one("res.users", string="Régularisé par", readonly=True, tracking=True)
    motif_refus = fields.Text(string="Motif de refus", tracking=True)

    can_validate_n1 = fields.Boolean(compute="_compute_access_flags")
    can_validate_tresorerie = fields.Boolean(compute="_compute_access_flags")
    can_validate_fi = fields.Boolean(compute="_compute_access_flags")
    can_validate_md = fields.Boolean(compute="_compute_access_flags")
    can_refuse = fields.Boolean(compute="_compute_access_flags")
    can_modify = fields.Boolean(compute="_compute_access_flags")
    can_edit_demande = fields.Boolean(compute="_compute_access_flags")
    can_saisir_depense = fields.Boolean(compute="_compute_access_flags")
    can_regulariser = fields.Boolean(compute="_compute_access_flags")

    @api.model
    def _default_employee(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.user.id)], limit=1)

    @api.depends("demandeur_id")
    def _compute_demandeur_user_id(self):
        for rec in self:
            rec.demandeur_user_id = rec.demandeur_id.user_id.id if rec.demandeur_id and rec.demandeur_id.user_id else False

    @api.depends("demandeur_id")
    def _compute_manager_n1_id(self):
        for rec in self:
            rec.manager_n1_id = rec.demandeur_id.parent_id.id if rec.demandeur_id else False

    @api.depends("demandeur_id")
    def _compute_department_id(self):
        for rec in self:
            rec.department_id = rec.demandeur_id.department_id.id if rec.demandeur_id else False

    @api.depends("line_ids.sous_total")
    def _compute_total_prix(self):
        for rec in self:
            total = sum(rec.line_ids.mapped("sous_total"))
            rec.total_prix = total
            rec.montant_demande = total
            amount_display = rec._format_amount_dh(total)
            rec.total_prix_display = amount_display
            rec.montant_demande_display = amount_display

    def _format_amount_dh(self, amount):
        return f"{amount:,.2f}".replace(",", " ").replace(".", ",") + " DH"

    @api.depends("montant_demande", "montant_depense")
    def _compute_montants_saisie(self):
        for rec in self:
            montant_a_rendre = max((rec.montant_demande or 0.0) - (rec.montant_depense or 0.0), 0.0)
            rec.montant_a_rendre = montant_a_rendre
            rec.montant_depense_display = rec._format_amount_dh(rec.montant_depense or 0.0)
            rec.montant_a_rendre_display = rec._format_amount_dh(montant_a_rendre)

    @api.depends(
        "state",
        "demandeur_user_id",
        "manager_n1_id.user_id",
        "tresorier_id",
        "validateur_fi_id",
        "validateur_md_prevu_id",
    )
    def _compute_access_flags(self):
        for rec in self:
            user = self.env.user
            is_manager_n1 = bool(rec.manager_n1_id.user_id and rec.manager_n1_id.user_id == user)
            is_tresorerie = bool(rec.tresorier_id and rec.tresorier_id == user)
            is_fi = bool(rec.validateur_fi_id and rec.validateur_fi_id == user)
            is_md = bool(rec.validateur_md_prevu_id and rec.validateur_md_prevu_id == user)

            rec.can_validate_n1 = (
                rec.state == "validation_n1"
                and is_manager_n1
                and user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_validateur_n1")
            )
            rec.can_validate_tresorerie = (
                rec.state == "tresorerie"
                and is_tresorerie
                and user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_tresorerie")
            )
            rec.can_validate_fi = (
                rec.state == "validation_fi"
                and is_fi
                and user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_validateur_fi")
            )
            rec.can_validate_md = (
                rec.state == "validation_md"
                and is_md
                and user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_validateur_md")
            )
            rec.can_refuse = rec.can_validate_n1 or rec.can_validate_tresorerie or rec.can_validate_fi or rec.can_validate_md
            rec.can_modify = (
                rec.demandeur_user_id == user
                or rec.can_validate_n1
                or rec.can_validate_tresorerie
                or rec.can_validate_fi
                or rec.can_validate_md
            )
            rec.can_edit_demande = rec.state == "expression_besoin" and rec.demandeur_user_id == user
            rec.can_saisir_depense = rec.state == "saisie" and rec.demandeur_user_id == user
            rec.can_regulariser = (
                rec.state == "regularisation"
                and is_tresorerie
                and user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_tresorerie")
            )

    @api.constrains("montant_demande", "line_ids")
    def _check_required_amount(self):
        for rec in self:
            if rec.state != "expression_besoin" and rec.montant_demande <= 0:
                raise ValidationError(_("Le montant demandé doit être supérieur à zéro."))

    @api.constrains("montant_depense")
    def _check_montant_depense(self):
        for rec in self:
            if rec.montant_depense < 0:
                raise ValidationError(_("Le montant dépensé ne peut pas être négatif."))

    @api.constrains("type_demande", "type_demande_autre")
    def _check_type_demande_autre(self):
        for rec in self:
            if rec.type_demande == "autre" and not rec.type_demande_autre:
                raise ValidationError(_("Le champ Autre type de demande est obligatoire lorsque le type de demande est Autre."))

    def _find_validation_rule(self):
        self.ensure_one()
        return self.env["ar.sortie.caisse.regle.validation"].search([
            ("active", "=", True),
            ("montant_min", "<=", self.montant_demande),
            ("montant_max", ">=", self.montant_demande),
        ], limit=1)

    def _clean_header(self, value):
        if not value:
            return False
        return str(value).replace("\n", "").replace("\r", "").strip()

    def _get_user_email(self, user):
        if not user:
            return False
        user = user.sudo()
        email = user.partner_id.email or user.email
        return self._clean_header(email) if email else False

    def _get_employee_email(self, employee):
        if not employee:
            return False
        employee = employee.sudo()
        email = False
        if employee.user_id:
            email = employee.user_id.partner_id.email or employee.user_id.email
        if not email:
            email = employee.work_email
        return self._clean_header(email) if email else False

    def _send_template(self, xmlid, email_to_list):
        self.ensure_one()
        template = self.env.ref(xmlid, raise_if_not_found=False)
        if not template:
            return
        recipients = [self._clean_header(email) for email in (email_to_list or [])]
        recipients = [email for email in recipients if email]
        if not recipients:
            return
        reply_to = self.env.user.partner_id.email or self.env.user.email or ""
        template.send_mail(self.id, force_send=True, email_values={
            "email_to": self._clean_header(",".join(recipients)),
            "reply_to": self._clean_header(reply_to),
        })

    def _send_to_demandeur(self, template_xmlid):
        self.ensure_one()
        email = self._get_employee_email(self.demandeur_id)
        if email:
            self._send_template(template_xmlid, [email])

    def _send_to_manager_n1(self, template_xmlid):
        self.ensure_one()
        email = self._get_employee_email(self.manager_n1_id)
        if email:
            self._send_template(template_xmlid, [email])

    def _send_to_current_fi(self, template_xmlid):
        self.ensure_one()
        email = self._get_user_email(self.validateur_fi_id)
        if email:
            self._send_template(template_xmlid, [email])

    def _send_to_tresorerie(self, template_xmlid):
        self.ensure_one()
        email = self._get_user_email(self.tresorier_id)
        if email:
            self._send_template(template_xmlid, [email])

    def _send_to_md(self, template_xmlid):
        self.ensure_one()
        email = self._get_user_email(self.validateur_md_prevu_id)
        if email:
            self._send_template(template_xmlid, [email])

    def _send_notification_for_current_state(self):
        self.ensure_one()
        if self.state == "validation_n1":
            self._send_to_manager_n1("ar_demande_sortie_caisse.mail_template_sortie_caisse_to_n1")
        elif self.state == "tresorerie":
            self._send_to_tresorerie("ar_demande_sortie_caisse.mail_template_sortie_caisse_to_tresorerie")
        elif self.state == "validation_fi":
            self._send_to_current_fi("ar_demande_sortie_caisse.mail_template_sortie_caisse_to_fi")
        elif self.state == "validation_md":
            self._send_to_md("ar_demande_sortie_caisse.mail_template_sortie_caisse_to_md")
        elif self.state == "saisie":
            self._send_to_demandeur("ar_demande_sortie_caisse.mail_template_sortie_caisse_to_saisie")
        elif self.state == "regularisation":
            self._send_to_tresorerie("ar_demande_sortie_caisse.mail_template_sortie_caisse_to_regularisation")
        elif self.state == "acceptee":
            self._send_to_demandeur("ar_demande_sortie_caisse.mail_template_sortie_caisse_accepted")
        elif self.state == "refusee":
            self._send_to_demandeur("ar_demande_sortie_caisse.mail_template_sortie_caisse_refused")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.is_superuser() and not self.env.user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_user"):
            raise AccessError(_("Vous n'avez pas le droit de créer une demande de sortie de caisse."))
        for vals in vals_list:
            if vals.get("name", "Nouveau") == "Nouveau":
                vals["name"] = self.env["ir.sequence"].next_by_code("ar.demande.sortie.caisse") or "Nouveau"
        return super().create(vals_list)

    def write(self, vals):
        if self.env.context.get("skip_sortie_caisse_access_check") or self.env.is_superuser():
            return super().write(vals)

        workflow_fields = {
            "state",
            "regle_validation_id",
            "tresorier_id",
            "validateur_fi_id",
            "validateur_md_prevu_id",
            "date_validation_n1",
            "date_validation_tresorerie",
            "date_validation_fi",
            "date_validation_md",
            "date_acceptation",
            "date_refus",
            "date_saisie",
            "date_regularisation",
            "validateur_n1_id",
            "validateur_tresorerie_id",
            "validateur_fi_done_id",
            "validateur_md_id",
            "saisie_user_id",
            "regularisateur_id",
            "motif_refus",
        }
        protected_fields = {
            "name",
            "demandeur_id",
            "demandeur_user_id",
            "manager_n1_id",
            "department_id",
            "date_demande",
            "montant_demande",
            "total_prix",
            "montant_a_rendre",
        }
        editable_fields = {
            "type_demande",
            "type_demande_autre",
            "description_demande",
            "attachment_ids",
            "line_ids",
        }
        saisie_fields = {
            "montant_depense",
            "justificatif_saisie_ids",
        }

        if set(vals).issubset({"motif_refus"}):
            for rec in self:
                if not rec.can_refuse:
                    raise AccessError(_("Vous n'avez pas le droit de renseigner le motif de refus."))
            return super().write(vals)

        if set(vals).intersection(workflow_fields):
            raise AccessError(_("Les changements du workflow doivent passer par les boutons de validation."))

        if set(vals).intersection(protected_fields):
            raise AccessError(_("Vous n'avez pas le droit de modifier les champs automatiques de la demande."))

        if set(vals).issubset(editable_fields):
            for rec in self:
                if not rec.can_edit_demande:
                    raise AccessError(_("Vous ne pouvez modifier la demande qu’à l’état Expression de besoin et uniquement si vous êtes le demandeur."))
            return super().write(vals)

        if set(vals).issubset(saisie_fields):
            for rec in self:
                if not rec.can_saisir_depense:
                    raise AccessError(_("Vous ne pouvez renseigner la saisie qu’à l’état Saisie et uniquement si vous êtes le demandeur."))
            return super().write(vals)

        return super().write(vals)

    def action_soumettre(self):
        for rec in self:
            if rec.state != "expression_besoin":
                continue
            if rec.demandeur_user_id != self.env.user:
                raise AccessError(_("Seul le demandeur peut soumettre cette demande."))
            if rec.montant_demande <= 0:
                raise ValidationError(_("Le montant demandé est obligatoire avant de soumettre la demande."))
            if not rec.line_ids:
                raise ValidationError(_("Vous devez ajouter au moins une ligne dans le tableau avant de soumettre la demande."))

            rule = rec._find_validation_rule()
            if not rule:
                raise ValidationError(_("Aucune règle de validation active ne couvre ce montant demandé."))

            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "regle_validation_id": rule.id,
                "tresorier_id": rule.tresorier_id.id,
                "validateur_fi_id": rule.validateur_fi_id.id,
                "validateur_md_prevu_id": rule.validateur_md_id.id,
                "state": "validation_n1",
            })
            rec._send_notification_for_current_state()

    def _is_current_user_real_manager_n1(self):
        self.ensure_one()
        return bool(self.manager_n1_id.user_id and self.manager_n1_id.user_id == self.env.user)

    def action_valider_n1(self):
        for rec in self:
            if not rec.can_validate_n1:
                raise AccessError(_("Vous n'avez pas le droit de valider cette demande au niveau N+1."))
            vals = {
                "date_validation_n1": fields.Datetime.now(),
                "validateur_n1_id": self.env.user.id,
            }
            if rec.validateur_fi_id:
                vals["state"] = "validation_fi"
            elif rec.tresorier_id:
                vals["state"] = "tresorerie"
            elif rec.validateur_md_prevu_id:
                vals["state"] = "validation_md"
            else:
                vals["state"] = "saisie"
            rec.with_context(skip_sortie_caisse_access_check=True).write(vals)
            rec.message_post(body=_("Validation N+1 effectuée par %s.") % self.env.user.display_name)
            rec._send_notification_for_current_state()

    def action_valider_tresorerie(self):
        for rec in self:
            if not rec.can_validate_tresorerie:
                raise AccessError(_("Vous n'avez pas le droit de valider cette demande au niveau Trésorerie."))
            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "date_validation_tresorerie": fields.Datetime.now(),
                "validateur_tresorerie_id": self.env.user.id,
                "state": "validation_md" if rec.validateur_md_prevu_id else "saisie",
            })
            rec.message_post(body=_("Validation Trésorerie effectuée par %s.") % self.env.user.display_name)
            rec._send_notification_for_current_state()

    def action_valider_fi(self):
        for rec in self:
            if not rec.can_validate_fi:
                raise AccessError(_("Vous n'avez pas le droit de valider cette demande au niveau FI."))
            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "date_validation_fi": fields.Datetime.now(),
                "validateur_fi_done_id": self.env.user.id,
                "state": "tresorerie" if rec.tresorier_id else ("validation_md" if rec.validateur_md_prevu_id else "saisie"),
            })
            rec.message_post(body=_("Validation FI effectuée par %s.") % self.env.user.display_name)
            rec._send_notification_for_current_state()

    def action_valider_md(self):
        for rec in self:
            if not rec.can_validate_md:
                raise AccessError(_("Vous n'avez pas le droit de valider cette demande au niveau MD."))
            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "date_validation_md": fields.Datetime.now(),
                "validateur_md_id": self.env.user.id,
                "state": "saisie",
            })
            rec.message_post(body=_("Validation MD effectuée par %s. Demande transmise au demandeur pour saisie.") % self.env.user.display_name)
            rec._send_notification_for_current_state()

    def action_confirmer_saisie(self):
        for rec in self:
            if not rec.can_saisir_depense:
                raise AccessError(_("Vous n'avez pas le droit de confirmer la saisie de cette demande."))
            if rec.montant_depense <= 0:
                raise ValidationError(_("Le montant dépensé doit être supérieur à zéro avant de confirmer la saisie."))
            if not rec.justificatif_saisie_ids:
                raise ValidationError(_("Vous devez ajouter les justificatifs avant de confirmer la saisie."))
            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "state": "regularisation",
                "date_saisie": fields.Datetime.now(),
                "saisie_user_id": self.env.user.id,
            })
            rec.message_post(body=_("Saisie confirmée par %s. Montant à rendre : %s. Demande transmise à la Trésorerie pour régularisation.") % (self.env.user.display_name, rec.montant_a_rendre_display))
            rec._send_notification_for_current_state()

    def action_regulariser(self):
        for rec in self:
            if not rec.can_regulariser:
                raise AccessError(_("Vous n'avez pas le droit de régulariser cette demande."))
            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "state": "acceptee",
                "date_regularisation": fields.Datetime.now(),
                "date_acceptation": fields.Datetime.now(),
                "regularisateur_id": self.env.user.id,
            })
            rec.message_post(body=_("Régularisation effectuée par %s. Demande archivée.") % self.env.user.display_name)
            rec._send_notification_for_current_state()

    def action_refuser(self):
        for rec in self:
            if not rec.can_refuse:
                raise AccessError(_("Vous n'avez pas le droit de refuser cette demande."))
            if not rec.motif_refus:
                raise ValidationError(_("Le champ Motif de refus est obligatoire avant de refuser la demande."))
            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "state": "refusee",
                "date_refus": fields.Datetime.now(),
            })
            rec.message_post(body=_("Demande refusée par %s. Motif : %s") % (self.env.user.display_name, rec.motif_refus))
            rec._send_notification_for_current_state()

    def action_demander_modification(self):
        for rec in self:
            if not rec.can_modify:
                raise AccessError(_("Vous n'avez pas le droit de modifier cette demande."))
            rec.with_context(skip_sortie_caisse_access_check=True).write({
                "state": "expression_besoin",
                "regle_validation_id": False,
                "tresorier_id": False,
                "validateur_fi_id": False,
                "validateur_md_prevu_id": False,
                "date_validation_n1": False,
                "date_validation_tresorerie": False,
                "date_validation_fi": False,
                "date_validation_md": False,
                "date_saisie": False,
                "date_regularisation": False,
                "date_acceptation": False,
                "date_refus": False,
                "validateur_n1_id": False,
                "validateur_tresorerie_id": False,
                "validateur_fi_done_id": False,
                "validateur_md_id": False,
                "saisie_user_id": False,
                "regularisateur_id": False,
                "motif_refus": False,
                "montant_depense": 0.0,
                "justificatif_saisie_ids": [(5, 0, 0)],
            })
            rec.message_post(body=_("La demande a été remise à l’état Expression de besoin."))
            rec._send_to_demandeur("ar_demande_sortie_caisse.mail_template_sortie_caisse_back_to_demandeur")

    def _open_action_wizard(self, action_type):
        self.ensure_one()
        return {
            "name": _("Confirmation"),
            "type": "ir.actions.act_window",
            "res_model": "ar.demande.sortie.caisse.action.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_demande_id": self.id,
                "default_action_type": action_type,
            },
        }

    def action_open_modify_wizard(self):
        return self._open_action_wizard("modify")

    def action_open_validate_n1_wizard(self):
        return self._open_action_wizard("validate_n1")

    def action_open_validate_tresorerie_wizard(self):
        return self._open_action_wizard("validate_tresorerie")

    def action_open_validate_fi_wizard(self):
        return self._open_action_wizard("validate_fi")

    def action_open_validate_md_wizard(self):
        return self._open_action_wizard("validate_md")

    def action_open_confirm_saisie_wizard(self):
        return self._open_action_wizard("confirm_saisie")

    def action_open_regulariser_wizard(self):
        return self._open_action_wizard("regulariser")

    def action_open_refuse_wizard(self):
        return self._open_action_wizard("refuse")


class ARDemandeSortieCaisseLine(models.Model):
    _name = "ar.demande.sortie.caisse.line"
    _description = "Ligne demande sortie caisse"
    _order = "id asc"

    demande_id = fields.Many2one(
        "ar.demande.sortie.caisse",
        string="Demande",
        required=True,
        ondelete="cascade",
    )
    commande = fields.Char(string="Commande", required=True)
    quantite = fields.Float(string="Quantité", required=True, default=1.0)
    prix = fields.Float(string="Prix", required=True)
    sous_total = fields.Float(string="Sous-total", compute="_compute_sous_total", store=True)

    @api.depends("quantite", "prix")
    def _compute_sous_total(self):
        for rec in self:
            rec.sous_total = rec.quantite * rec.prix

    @api.constrains("quantite", "prix")
    def _check_positive_values(self):
        for rec in self:
            if rec.quantite <= 0:
                raise ValidationError(_("La quantité doit être supérieure à zéro."))
            if rec.prix < 0:
                raise ValidationError(_("Le prix doit être positif."))

    def _check_demandeur_access(self):
        for rec in self:
            if rec.demande_id and not rec.demande_id.can_edit_demande:
                raise AccessError(_("Seul le demandeur peut modifier les lignes à l’état Expression de besoin."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            demande = self.env["ar.demande.sortie.caisse"].browse(vals.get("demande_id"))
            if demande and not demande.can_edit_demande:
                raise AccessError(_("Seul le demandeur peut ajouter des lignes à l’état Expression de besoin."))
        return super().create(vals_list)

    def write(self, vals):
        self._check_demandeur_access()
        return super().write(vals)

    def unlink(self):
        self._check_demandeur_access()
        return super().unlink()
