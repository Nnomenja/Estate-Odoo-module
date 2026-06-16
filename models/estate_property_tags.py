from odoo import models, fields

class EstatePropertyTags(models.Model):
    _name = "estate.property.tags"
    _description = "Estate Property Tags"


    # -------------------------------------------------------------------------
    # FIELDS 
    # -------------------------------------------------------------------------

    name = fields.Char(required=True, string="Property Tags")


    # -------------------------------------------------------------------------
    # SQL CONSTRAINTS 
    # -------------------------------------------------------------------------
    
    _unique_tag_name = models.Constraint(
        'UNIQUE(name)',
        'Tag name must be unique.'
    )
