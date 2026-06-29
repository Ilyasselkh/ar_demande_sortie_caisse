from odoo import api, fields, models, _


class ARDemandeSortieCaisseAIConfigWizard(models.TransientModel):
    _name = "ar.demande.sortie.caisse.ai.config.wizard"
    _description = "Configuration agent IA sortie caisse"

    openai_api_key = fields.Char(string="Clé API OpenAI")
    openai_model = fields.Char(string="Modèle OpenAI", default="gpt-5.4-mini")

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        params = self.env["ir.config_parameter"].sudo()
        vals.update({
            "openai_api_key": params.get_param("ar_demande_sortie_caisse.openai_api_key", ""),
            "openai_model": params.get_param("ar_demande_sortie_caisse.openai_model", "gpt-5.4-mini"),
        })
        return vals

    def action_save(self):
        self.ensure_one()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("ar_demande_sortie_caisse.openai_api_key", self.openai_api_key or "")
        params.set_param("ar_demande_sortie_caisse.openai_model", self.openai_model or "gpt-5.4-mini")
        return {"type": "ir.actions.act_window_close"}
