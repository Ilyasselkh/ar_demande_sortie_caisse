import json
import urllib.error
import urllib.request

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ARDemandeSortieCaisseAICreateWizard(models.TransientModel):
    _name = "ar.demande.sortie.caisse.ai.create.wizard"
    _description = "Chatbot IA création demande sortie caisse"

    prompt = fields.Text(
        string="Ancien message",
    )
    message_ids = fields.One2many(
        "ar.demande.sortie.caisse.ai.chat.message.wizard",
        "wizard_id",
        string="Conversation",
        readonly=True,
    )
    user_message = fields.Text(
        string="Message",
        placeholder="Écrivez votre demande ou répondez à la question de l'agent...",
    )
    ready_to_create = fields.Boolean(string="Demande prête", readonly=True)
    type_demande = fields.Selection([
        ("cas_urgence", "Cas d'urgence"),
        ("reception_boissons", "Repas"),
        ("moyens_generaux", "Moyens généraux"),
        ("poste", "Envoi Postal"),
        ("indemnite_rh", "Indemnité RH"),
        ("maintenance", "Maintenance"),
        ("autre", "Autre"),
    ], string="Type de demande")
    type_demande_autre = fields.Char(string="Autre type de demande")
    description_demande = fields.Text(string="Description")
    line_ids = fields.One2many(
        "ar.demande.sortie.caisse.ai.create.line.wizard",
        "wizard_id",
        string="Lignes proposées",
    )
    missing_info = fields.Text(string="Informations manquantes", readonly=True)
    agent_reasoning = fields.Text(string="Analyse de l'agent", readonly=True)
    confidence = fields.Selection([
        ("low", "Faible"),
        ("medium", "Moyenne"),
        ("high", "Élevée"),
    ], string="Confiance", readonly=True)
    raw_response = fields.Text(string="Réponse technique", readonly=True)

    @api.model
    def _check_user_can_create_ai_request(self):
        if not self.env.user.has_group("ar_demande_sortie_caisse.group_demande_sortie_caisse_user"):
            raise AccessError(_("Vous n'avez pas le droit de créer une demande via l'agent IA."))

    def action_analyze(self):
        return self.action_send_message()

    def action_send_message(self):
        self.ensure_one()
        self._check_user_can_create_ai_request()
        message = (self.user_message or self.prompt or "").strip()
        if not message:
            raise ValidationError(_("Veuillez écrire un message pour le chatbot."))
        self.env["ar.demande.sortie.caisse.ai.chat.message.wizard"].create({
            "wizard_id": self.id,
            "role": "user",
            "content": message,
        })
        result = self._call_openai_agent()
        self._apply_agent_result(result)
        self.user_message = False
        self.prompt = False
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_create_demande(self):
        self.ensure_one()
        self._check_user_can_create_ai_request()
        if not self.type_demande:
            raise ValidationError(_("L'agent n'a pas identifié le type de demande."))
        if self.type_demande == "autre" and not self.type_demande_autre:
            raise ValidationError(_("Veuillez préciser le type de demande lorsque le type est Autre."))
        if not self.description_demande:
            raise ValidationError(_("La description de la demande est obligatoire."))
        if not self.line_ids:
            raise ValidationError(_("L'agent doit proposer au moins une ligne avant de créer la demande."))
        if not self.ready_to_create:
            raise ValidationError(_("La demande n'est pas encore complète. Continuez la conversation avec l'agent."))

        demande = self.env["ar.demande.sortie.caisse"].create({
            "type_demande": self.type_demande,
            "type_demande_autre": self.type_demande_autre,
            "description_demande": self.description_demande,
            "line_ids": [(0, 0, {
                "commande": line.commande,
                "quantite": line.quantite,
                "prix": line.prix,
            }) for line in self.line_ids],
        })
        demande.message_post(body=_("Demande créée par le chatbot IA après conversation avec l'utilisateur."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "ar.demande.sortie.caisse",
            "res_id": demande.id,
            "view_mode": "form",
            "target": "current",
        }

    def _apply_agent_result(self, result):
        self.ensure_one()
        lines = result.get("lines") or []
        self.line_ids.unlink()
        assistant_message = result.get("assistant_message") or _("J'ai mis à jour le brouillon de votre demande.")
        self.env["ar.demande.sortie.caisse.ai.chat.message.wizard"].create({
            "wizard_id": self.id,
            "role": "assistant",
            "content": assistant_message,
        })
        self.write({
            "type_demande": result.get("type_demande") or "autre",
            "type_demande_autre": result.get("type_demande_autre") or False,
            "description_demande": result.get("description_demande") or self.description_demande,
            "missing_info": "\n".join("- %s" % item for item in result.get("missing_info", []) if item),
            "agent_reasoning": result.get("agent_reasoning") or "",
            "confidence": result.get("confidence") or "medium",
            "ready_to_create": bool(result.get("ready_to_create")),
            "raw_response": json.dumps(result, ensure_ascii=False, indent=2),
            "line_ids": [(0, 0, {
                "commande": line.get("commande") or _("Ligne à préciser"),
                "quantite": float(line.get("quantite") or 1.0),
                "prix": float(line.get("prix") or 0.0),
            }) for line in lines],
        })

    def _call_openai_agent(self):
        self.ensure_one()
        api_key = self.env["ir.config_parameter"].sudo().get_param("ar_demande_sortie_caisse.openai_api_key")
        model = self.env["ir.config_parameter"].sudo().get_param(
            "ar_demande_sortie_caisse.openai_model",
            "gpt-5.4-mini",
        )
        if not api_key:
            raise UserError(_("Veuillez configurer la clé API OpenAI dans Paramétrage > Agent IA."))

        conversation_input = [{
            "role": "system",
            "content": [{
                "type": "input_text",
                "text": self._get_system_prompt(),
            }],
        }]
        for message in self.message_ids.sorted("id"):
            conversation_input.append({
                "role": "assistant" if message.role == "assistant" else "user",
                "content": [{
                    "type": "input_text",
                    "text": message.content or "",
                }],
            })

        payload = {
            "model": model,
            "input": conversation_input,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "sortie_caisse_request",
                    "strict": True,
                    "schema": self._get_response_schema(),
                },
            },
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer %s" % api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="ignore")
            raise UserError(_("Erreur OpenAI : %s") % details) from error
        except Exception as error:
            raise UserError(_("Impossible de contacter l'agent IA : %s") % error) from error

        text = self._extract_response_text(response_data)
        try:
            return json.loads(text)
        except json.JSONDecodeError as error:
            raise UserError(_("L'agent IA n'a pas retourné un JSON valide : %s") % text) from error

    def _extract_response_text(self, response_data):
        if response_data.get("output_text"):
            return response_data["output_text"]
        for item in response_data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in ("output_text", "text") and content.get("text"):
                    return content["text"]
        raise UserError(_("Réponse OpenAI vide ou non exploitable."))

    def _get_system_prompt(self):
        return _(
            "Tu es un chatbot métier Odoo pour créer des demandes de sortie de caisse. "
            "Tu dois dialoguer avec l'utilisateur jusqu'à obtenir une demande complète. "
            "Pose une seule question claire à la fois quand une information manque. "
            "Maintiens un brouillon structuré à partir de toute la conversation. "
            "Ne valide jamais la demande. Ne soumets jamais la demande. "
            "Quand la demande est complète, indique que l'utilisateur peut cliquer sur Créer la demande. "
            "Utilise uniquement les types autorisés : cas_urgence, reception_boissons, "
            "moyens_generaux, poste, indemnite_rh, maintenance, autre. "
            "Une demande est complète seulement si type_demande, description_demande et au moins une ligne "
            "avec commande, quantité et prix sont disponibles. "
            "Les montants sont en dirhams marocains. Retourne strictement le JSON demandé."
        )

    def _get_response_schema(self):
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type_demande": {
                    "type": "string",
                    "enum": [
                        "cas_urgence",
                        "reception_boissons",
                        "moyens_generaux",
                        "poste",
                        "indemnite_rh",
                        "maintenance",
                        "autre",
                    ],
                },
                "type_demande_autre": {"type": "string"},
                "description_demande": {"type": "string"},
                "assistant_message": {"type": "string"},
                "ready_to_create": {"type": "boolean"},
                "lines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "commande": {"type": "string"},
                            "quantite": {"type": "number"},
                            "prix": {"type": "number"},
                        },
                        "required": ["commande", "quantite", "prix"],
                    },
                },
                "missing_info": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "agent_reasoning": {"type": "string"},
                "confidence": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                },
            },
            "required": [
                "type_demande",
                "type_demande_autre",
                "description_demande",
                "assistant_message",
                "ready_to_create",
                "lines",
                "missing_info",
                "agent_reasoning",
                "confidence",
            ],
        }


class ARDemandeSortieCaisseAIChatMessageWizard(models.TransientModel):
    _name = "ar.demande.sortie.caisse.ai.chat.message.wizard"
    _description = "Message chatbot IA sortie caisse"
    _order = "id asc"

    wizard_id = fields.Many2one(
        "ar.demande.sortie.caisse.ai.create.wizard",
        string="Assistant",
        required=True,
        ondelete="cascade",
    )
    role = fields.Selection([
        ("user", "Utilisateur"),
        ("assistant", "Assistant IA"),
    ], string="Rôle", required=True)
    content = fields.Text(string="Message", required=True)


class ARDemandeSortieCaisseAICreateLineWizard(models.TransientModel):
    _name = "ar.demande.sortie.caisse.ai.create.line.wizard"
    _description = "Ligne agent IA création demande sortie caisse"

    wizard_id = fields.Many2one(
        "ar.demande.sortie.caisse.ai.create.wizard",
        string="Assistant",
        required=True,
        ondelete="cascade",
    )
    commande = fields.Char(string="Description de besoin", required=True)
    quantite = fields.Float(string="Quantité", required=True, default=1.0)
    prix = fields.Float(string="Prix unitaire", required=True)
    sous_total = fields.Float(string="Sous-total", compute="_compute_sous_total")

    @api.depends("quantite", "prix")
    def _compute_sous_total(self):
        for rec in self:
            rec.sous_total = rec.quantite * rec.prix
