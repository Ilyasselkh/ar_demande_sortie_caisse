from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ARSortieCaisseRegleValidation(models.Model):
    _name = "ar.sortie.caisse.regle.validation"
    _description = "Règle de validation sortie caisse"
    _order = "montant_min asc, id asc"

    name = fields.Char(string="Nom", compute="_compute_name", store=True)
    montant_min = fields.Float(string="Prix de", required=True)
    montant_max = fields.Float(string="Prix à", required=True)
    active = fields.Boolean(default=True)
    tresorier_id = fields.Many2one("res.users", string="Trésorerie")
    validateur_fi_id = fields.Many2one("res.users", string="Validation FI")
    validateur_md_id = fields.Many2one("res.users", string="Validation MD")

    @api.depends("montant_min", "montant_max")
    def _compute_name(self):
        for rec in self:
            rec.name = _("%s a %s") % (rec.montant_min or 0.0, rec.montant_max or 0.0)

    @api.constrains("montant_min", "montant_max")
    def _check_amounts(self):
        for rec in self:
            if rec.montant_min < 0 or rec.montant_max < 0:
                raise ValidationError(_("Les montants doivent être positifs."))
            if rec.montant_max < rec.montant_min:
                raise ValidationError(_("Le prix à doit être supérieur ou égal au prix de."))

    @api.constrains("tresorier_id", "validateur_fi_id", "validateur_md_id")
    def _check_unique_validators(self):
        for rec in self:
            validators = [
                rec.tresorier_id.id,
                rec.validateur_fi_id.id,
                rec.validateur_md_id.id,
            ]
            validators = [validator for validator in validators if validator]
            if len(validators) != len(set(validators)):
                raise ValidationError(_("Un validateur ne peut pas être affecté plusieurs fois sur la même règle."))

    @api.constrains("montant_min", "montant_max", "active")
    def _check_no_overlap(self):
        for rec in self:
            if not rec.active:
                continue
            overlap = self.search([
                ("id", "!=", rec.id),
                ("active", "=", True),
                ("montant_min", "<=", rec.montant_max),
                ("montant_max", ">=", rec.montant_min),
            ], limit=1)
            if overlap:
                raise ValidationError(_("Cette tranche de prix chevauche une autre règle active."))

    def get_validators(self):
        self.ensure_one()
        return self.tresorier_id | self.validateur_fi_id | self.validateur_md_id
