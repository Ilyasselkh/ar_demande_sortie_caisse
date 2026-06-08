from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ARDemandeSortieCaisseActionWizard(models.TransientModel):
    _name = "ar.demande.sortie.caisse.action.wizard"
    _description = "Confirmation action demande sortie caisse"

    demande_id = fields.Many2one("ar.demande.sortie.caisse", string="Demande", required=True, readonly=True)
    action_type = fields.Selection([
        ("modify", "Modifier"),
        ("validate_n1", "Valider N+1"),
        ("validate_tresorerie", "Valider Trésorerie"),
        ("validate_fi", "Valider FI"),
        ("validate_md", "Valider MD"),
        ("confirm_saisie", "Confirmer la saisie"),
        ("regulariser", "Régulariser"),
        ("refuse", "Refuser"),
    ], string="Type d'action", required=True, readonly=True)
    motif_refus = fields.Text(string="Motif de refus")

    def action_confirm(self):
        self.ensure_one()
        if not self.demande_id:
            raise ValidationError(_("Aucune demande sélectionnée."))

        if self.action_type == "modify":
            self.demande_id.action_demander_modification()
        elif self.action_type == "validate_n1":
            self.demande_id.action_valider_n1()
        elif self.action_type == "validate_tresorerie":
            self.demande_id.action_valider_tresorerie()
        elif self.action_type == "validate_fi":
            self.demande_id.action_valider_fi()
        elif self.action_type == "validate_md":
            self.demande_id.action_valider_md()
        elif self.action_type == "confirm_saisie":
            self.demande_id.action_confirmer_saisie()
        elif self.action_type == "regulariser":
            self.demande_id.action_regulariser()
        elif self.action_type == "refuse":
            if not self.motif_refus:
                raise ValidationError(_("Le champ Motif de refus est obligatoire avant de refuser la demande."))
            self.demande_id.write({"motif_refus": self.motif_refus})
            self.demande_id.action_refuser()
        else:
            raise ValidationError(_("Action inconnue."))

        return {"type": "ir.actions.act_window_close"}
