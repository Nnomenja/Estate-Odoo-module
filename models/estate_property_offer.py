from odoo import models, fields, api
from datetime import timedelta, date
from colorama import init, Fore


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float()
    status = fields.Selection(copy=False, selection=[('Accepted', 'Accepted'), ('Refused', 'Refused')])
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True)
    property_id = fields.Many2one(comodel_name="estate.property", string="Property", required=True)
    validity = fields.Integer(string="Validity (days)", default=7, store=True)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", string="Deadline")

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            # print(Fore.GREEN + f"Compute method called for record ID {record.id} with validity {record.validity}" + Fore.RESET)
            create_date = record.create_date.date() if record.create_date else date.today()
            record.date_deadline = create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            validity_days = (record.date_deadline - record.create_date.date()).days if record.create_date else 0
            
            record.validity = validity_days if validity_days >= 0 else 0
    