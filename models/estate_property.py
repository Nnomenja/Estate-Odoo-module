from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char(required=True, string="Title")
    description = fields.Text(string="Description")
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Date.today() + relativedelta(months=3), string="Available From" )
    expected_price = fields.Float(required=True, string="Expected Price")
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2, string="Bedrooms")
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean()
    garden = fields.Boolean()   
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('North', 'North'), ('South', 'South'), ('East', 'East'), ('West', 'West')]
    )
    active = fields.Boolean(default=False)
    state = fields.Selection(
        string="Status",
        default="New",
        required=True,
        selection=[('New', 'New'), ('Offer Received', 'Offer Received'), ('Offer Accepted', 'Offer Accepted'), ('Sold', 'Sold'), ('Cancelled', 'Cancelled')]
    )
    property_type_id = fields.Many2one(comodel_name="estate.property.type", string="Property Type")
    property_tags_id = fields.Many2many(comodel_name="estate.property.tags", string="Property Tags")
    salesman_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="Salesman")
    buyer_id = fields.Many2one(comodel_name="res.partner", string="Buyer")
    offer_ids = fields.One2many(comodel_name="estate.property.offer", inverse_name="property_id", string="Offers")

    total_area = fields.Float(compute="_compute_total_area", string="Total Area (sqm)", readonly=True)
    best_offer_price = fields.Float(compute="_compute_best_price", string="Best Offer", readonly=True)
    # -------------------------------------------------------------------------
    # DEPENDS METHODS
    # -------------------------------------------------------------------------

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_offer_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_offer_price = 0.0