from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"


    # -------------------------------------------------------------------------
    # FIELDS 
    # -------------------------------------------------------------------------

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
    # SQL CONSTRAINTS 
    # -------------------------------------------------------------------------
    
    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'Expected price must be greater than 0.'
    )

    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'Selling price cannot be negative.'
    )


    # -------------------------------------------------------------------------
    # PYTHON CONSTRAINTS 
    # -------------------------------------------------------------------------
    
    @api.constrains("selling_price", "expected_price")
    def _check_prices(self):
        for record in self:
            if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0 or  record.selling_price <= 0:
                raise UserError("Selling price cannot be less than 90% of the expected price.")


    # -------------------------------------------------------------------------
    # BUTTON FORM METHODS
    # -------------------------------------------------------------------------
    
    def on_status_cancel(self):
        for record in self:
            if record.state == "Sold":
                raise UserError("You cannot cancel a sold property.")
            record.state = "Cancelled"

    def on_status_sold(self):
        for record in self:
            if record.state == "Cancelled":
                raise UserError("You cannot sell a cancelled property.")
            record.state = "Sold"


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
    
    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = "North"
            else:
                record.garden_area = 0
                record.garden_orientation = False
