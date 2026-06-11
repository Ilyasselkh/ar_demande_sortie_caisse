from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ARSortieCaisseBudget(models.Model):
    _name = "ar.sortie.caisse.budget"
    _description = "Budget sortie caisse"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Nom", required=True, default="Budget", tracking=True)
    montant_budget = fields.Float(string="Budget", required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("montant_budget")
    def _check_budget_values(self):
        for rec in self:
            if rec.montant_budget < 0:
                raise ValidationError(_("Le budget doit être positif."))

    @api.constrains("active")
    def _check_single_active_budget(self):
        for rec in self:
            if not rec.active:
                continue
            active_budget = self.search([
                ("id", "!=", rec.id),
                ("active", "=", True),
            ], limit=1)
            if active_budget:
                raise ValidationError(_("Un seul budget actif est autorisé."))

    @api.model
    def _get_active_budget(self):
        return self.search([("active", "=", True)], limit=1)
