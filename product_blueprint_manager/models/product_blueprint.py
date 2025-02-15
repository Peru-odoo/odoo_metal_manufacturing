from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductBlueprint(models.Model):
    _name = 'product.blueprint'
    _description = 'Product Blueprint'

    name = fields.Char('Nombre del Plano', required=True)
    file = fields.Binary('Archivo del Plano', required=True, attachment=True)
    filename = fields.Char('Nombre del Archivo', compute='_compute_filename', store=True)
    product_id = fields.Many2one('product.template', string='Producto', required=True)
    formula_ids = fields.One2many('product.blueprint.formula', 'blueprint_id', string='Fórmulas')

    @api.depends('file', 'name')
    def _compute_filename(self):
        """Compute the filename based on the blueprint name."""
        for record in self:
            if record.file and record.name:
                record.filename = record.name + ".svg"
            else:
                record.filename = ''

class ProductBlueprintFormula(models.Model):
    _name = 'product.blueprint.formula'
    _description = 'Fórmula del Plano de Producto'
    COLOR_OPTIONS = [
        ('black', 'Negro'),
        ('white', 'Blanco'),
        ('red', 'Rojo'),
        ('green', 'Verde'),
        ('blue', 'Azul'),
        ('yellow', 'Amarillo'),
        ('magenta', 'Magenta'),
        ('cyan', 'Cian'),
        ('gray', 'Gris'),
    ]

    name = fields.Char('Nombre de la Fórmula', required=True)
    formula_expression = fields.Char('Expresión de la Fórmula', required=True)
    product_id = fields.Many2one('product.template', string='Producto', required=True)
    blueprint_id = fields.Many2one('product.blueprint', string='Plano', required=True, help="El plano al que pertenece esta fórmula.", ondelete='cascade')
    position_x = fields.Float('Posición X (mm)', required=True, help="La coordenada X en milímetros para posicionar la fórmula en el plano.")
    position_y = fields.Float('Posición Y (mm)', required=True, help="La coordenada Y en milímetros para posicionar la fórmula en el plano.")
    available_attributes = fields.Char(string="Atributos Disponibles", compute="_compute_available_attributes", store=False, help="Atributos disponibles para usar en la fórmula (separados por comas).")
    font_size = fields.Char('Tamaño de la fuente (mm)', default='4')
    font_color = fields.Selection(COLOR_OPTIONS, string='Color de la Fuente', default='black', help="Nombre del color de la fuente.")

    @api.depends('product_id')
    def _compute_available_attributes(self):
        """Compute available attributes for use in the formula."""
        for record in self:
            if record.product_id:
                custom_attribute_values = record.product_id.valid_product_template_attribute_line_ids.mapped('attribute_id.value_ids').filtered(lambda v: v.is_custom)
                variable_names = [value.name for value in custom_attribute_values]
                record.available_attributes = ', '.join(variable_names)
            else:
                record.available_attributes = ''

    @api.constrains('blueprint_id')
    def _check_blueprint_id(self):
        for record in self:
            if not record.blueprint_id:
                raise ValidationError(f"La fórmula '{record.name}' debe estar asociada a un plano.")
