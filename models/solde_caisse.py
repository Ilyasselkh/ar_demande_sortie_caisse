from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError


class ARSortieCaisseSolde(models.Model):
    _name = "ar.sortie.caisse.solde"
    _description = "Solde de caisse"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Nom", required=True, default="Caisse principale", tracking=True)
    solde_courant = fields.Float(string="Solde de caisse", tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    can_manage_active = fields.Boolean(compute="_compute_can_manage_active")
    mouvement_ids = fields.One2many(
        "ar.sortie.caisse.mouvement",
        "solde_id",
        string="Historique",
        readonly=True,
    )
    alimentation_type = fields.Selection([
        ("reste_regularisation", "Rendu après régularisation"),
        ("vente_dechets", "Vente déchets"),
        ("banque", "Alimentation depuis la banque"),
        ("annulation_demande", "Annulation de la demande"),
        ("autre", "Autre alimentation"),
    ], string="Type d'alimentation")
    alimentation_montant = fields.Float(string="Montant à alimenter")
    alimentation_note = fields.Text(string="Note alimentation")

    def _compute_can_manage_active(self):
        can_manage = self.env.is_superuser() or self.env.user.has_group("base.group_system")
        for rec in self:
            rec.can_manage_active = can_manage

    @api.model
    def _check_tresorerie_access(self):
        if self.env.is_superuser():
            return
        if self.env.user.has_group("base.group_system"):
            return
        if not self.env.user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_tresorerie"):
            raise AccessError(_("Seule la Trésorerie peut gérer le solde de caisse."))

    @api.model
    def _get_active_solde(self):
        solde = self.search([("active", "=", True)], limit=1)
        if not solde:
            raise ValidationError(_("Veuillez créer un Solde de Caisse actif avant de valider une sortie de caisse."))
        return solde

    @api.constrains("active")
    def _check_single_active_solde(self):
        for rec in self:
            if not rec.active:
                continue
            active_solde = self.search([
                ("id", "!=", rec.id),
                ("active", "=", True),
            ], limit=1)
            if active_solde:
                raise ValidationError(_("Un seul solde de caisse actif est autorisé."))

    @api.model_create_multi
    def create(self, vals_list):
        self._check_tresorerie_access()
        initial_amounts = []
        for vals in vals_list:
            initial_amounts.append(vals.get("solde_courant") or 0.0)
            vals["solde_courant"] = 0.0
        records = super().create(vals_list)
        for record, amount in zip(records, initial_amounts):
            if amount:
                record._create_mouvement(
                    "augmentation",
                    amount,
                    alimentation_type="autre",
                    note=_("Solde initial"),
                )
        return records

    def write(self, vals):
        self._check_tresorerie_access()
        if "active" in vals and not self.env.is_superuser() and not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Seul un administrateur peut modifier le champ Active."))
        if "solde_courant" in vals and not self.env.context.get("skip_solde_caisse_write_check"):
            raise AccessError(_("Le solde doit être modifié par un mouvement de caisse."))
        return super().write(vals)

    def unlink(self):
        self._check_tresorerie_access()
        if self.mapped("mouvement_ids"):
            raise ValidationError(_("Vous ne pouvez pas supprimer un solde qui contient des mouvements."))
        return super().unlink()

    def action_alimenter(self):
        for rec in self:
            rec._check_tresorerie_access()
            if rec.alimentation_montant <= 0:
                raise ValidationError(_("Le montant à alimenter doit être supérieur à zéro."))
            if not rec.alimentation_type:
                raise ValidationError(_("Le type d'alimentation est obligatoire."))
            rec._create_mouvement(
                "augmentation",
                rec.alimentation_montant,
                alimentation_type=rec.alimentation_type,
                note=rec.alimentation_note,
            )
            rec.with_context(skip_solde_caisse_write_check=True).write({
                "alimentation_montant": 0.0,
                "alimentation_type": False,
                "alimentation_note": False,
            })
        return True

    def _create_mouvement(self, mouvement_type, montant, alimentation_type=False, demande_id=False, note=False):
        self.ensure_one()
        if montant <= 0:
            raise ValidationError(_("Le montant du mouvement doit être supérieur à zéro."))
        if mouvement_type == "augmentation" and not alimentation_type:
            raise ValidationError(_("Le type d'alimentation est obligatoire pour une augmentation."))

        solde_avant = self.solde_courant
        if mouvement_type == "deduction":
            solde_apres = solde_avant - montant
            if solde_apres < 0:
                self._notify_solde_caisse_alert(
                    _("Solde de caisse insuffisant"),
                    montant,
                    solde_avant,
                    demande_id=demande_id,
                    commit=True,
                    message=_(
                        "Le solde de caisse est insuffisant pour effectuer cette sortie. "
                        "Veuillez alimenter la caisse avant de continuer."
                    ),
                )
                raise ValidationError(_("Le solde de caisse est insuffisant pour cette opération."))
        else:
            solde_apres = solde_avant + montant

        mouvement = self.env["ar.sortie.caisse.mouvement"].sudo().create({
            "solde_id": self.id,
            "mouvement_type": mouvement_type,
            "alimentation_type": alimentation_type,
            "montant": montant,
            "solde_avant": solde_avant,
            "solde_apres": solde_apres,
            "demande_id": demande_id,
            "user_id": self.env.user.id,
            "note": note,
        })
        self.with_context(skip_solde_caisse_write_check=True).sudo().write({"solde_courant": solde_apres})
        if mouvement_type == "deduction" and solde_apres <= 0:
            self._notify_solde_caisse_alert(
                _("Solde de caisse à zéro"),
                montant,
                solde_apres,
                demande_id=demande_id,
                message=_(
                    "Le solde de caisse est maintenant à zéro. "
                    "Veuillez alimenter la caisse avant les prochaines sorties."
                ),
            )
        return mouvement

    def _get_alert_users(self, demande=False):
        users = self.env["res.users"]
        if demande:
            users |= demande.tresorier_id
            users |= demande.validateur_fi_id

        tresorerie_group = self.env.ref(
            "ar_demande_sortie_caisse.group_demande_sortie_caisse_tresorerie",
            raise_if_not_found=False,
        )
        fi_group = self.env.ref(
            "ar_demande_sortie_caisse.group_demande_sortie_caisse_validateur_fi",
            raise_if_not_found=False,
        )
        if (not demande or not demande.tresorier_id) and tresorerie_group:
            users |= tresorerie_group.users
        if (not demande or not demande.validateur_fi_id) and fi_group:
            users |= fi_group.users
        return users.filtered(lambda user: user.partner_id)

    def _notify_solde_caisse_alert(self, subject, montant, solde, demande_id=False, message=False, commit=False):
        self.ensure_one()
        demande = self.env["ar.demande.sortie.caisse"].browse(demande_id).exists() if demande_id else False
        users = self._get_alert_users(demande)
        partner_ids = users.mapped("partner_id").ids
        if not partner_ids:
            return

        demande_line = ""
        if demande:
            demande_line = "<p><b>Demande liée :</b> %s</p>" % demande.name
        body = """
            <div>
                <p>Bonjour,</p>
                <p>%s</p>
                %s
                <p><b>Montant concerné :</b> %.2f</p>
                <p><b>Solde actuel :</b> %.2f</p>
            </div>
        """ % (message or subject, demande_line, montant, solde)

        self.sudo().message_post(
            body=body,
            subject=subject,
            partner_ids=partner_ids,
            message_type="notification",
            subtype_xmlid="mail.mt_comment",
        )
        if demande:
            demande.sudo().message_post(
                body=body,
                subject=subject,
                partner_ids=partner_ids,
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
            )
        if commit:
            self.env.cr.commit()


class ARSortieCaisseMouvement(models.Model):
    _name = "ar.sortie.caisse.mouvement"
    _description = "Mouvement de caisse"
    _order = "date_mouvement desc, id desc"

    name = fields.Char(string="Reference", compute="_compute_name", store=True)
    solde_id = fields.Many2one(
        "ar.sortie.caisse.solde",
        string="Solde de caisse",
        required=True,
        ondelete="cascade",
    )
    date_mouvement = fields.Datetime(string="Date", default=fields.Datetime.now, readonly=True)
    mouvement_type = fields.Selection([
        ("augmentation", "Augmentation"),
        ("deduction", "Déduction"),
    ], string="Type de mouvement", required=True, readonly=True)
    alimentation_type = fields.Selection([
        ("reste_regularisation", "Rendu après régularisation"),
        ("vente_dechets", "Vente déchets"),
        ("banque", "Alimentation depuis la banque"),
        ("annulation_demande", "Annulation de la demande"),
        ("autre", "Autre alimentation"),
    ], string="Type d'alimentation", readonly=True)
    montant = fields.Float(string="Montant", required=True, readonly=True)
    solde_avant = fields.Float(string="Solde avant", readonly=True)
    solde_apres = fields.Float(string="Solde après", readonly=True)
    demande_id = fields.Many2one("ar.demande.sortie.caisse", string="Demande liée", readonly=True)
    user_id = fields.Many2one("res.users", string="Utilisateur", default=lambda self: self.env.user, readonly=True)
    note = fields.Text(string="Note", readonly=True)

    @api.depends("mouvement_type", "date_mouvement", "demande_id")
    def _compute_name(self):
        labels = dict(self._fields["mouvement_type"].selection)
        for rec in self:
            origin = rec.demande_id.name if rec.demande_id else fields.Datetime.to_string(rec.date_mouvement or fields.Datetime.now())
            rec.name = "%s - %s" % (labels.get(rec.mouvement_type, ""), origin)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.is_superuser() and not self.env.user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_tresorerie"):
            raise AccessError(_("Seule la Trésorerie peut créer des mouvements de caisse."))
        return super().create(vals_list)

    def write(self, vals):
        if self.env.context.get("skip_caisse_mouvement_write_check"):
            return super().write(vals)
        raise AccessError(_("Les mouvements de caisse ne peuvent pas être modifiés."))

    def unlink(self):
        raise AccessError(_("Les mouvements de caisse ne peuvent pas être supprimés."))

    @api.model
    def _fix_existing_accented_notes(self):
        replacements = {
            "apres regularisation": "après régularisation",
            "Reste rendu après régularisation": "Rendu après régularisation",
            "suite a la modification": "suite à la modification",
            "Solde de caisse a zero": "Solde de caisse à zéro",
            "Demande liee": "Demande liée",
            "Montant concerne": "Montant concerné",
        }
        movements = self.sudo().search([("note", "!=", False)])
        for movement in movements:
            note = movement.note or ""
            fixed_note = note
            for old, new in replacements.items():
                fixed_note = fixed_note.replace(old, new)
            if fixed_note != note:
                movement.with_context(skip_caisse_mouvement_write_check=True).sudo().write({"note": fixed_note})
