from odoo import models, fields
from odoo import api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
from odoo.exceptions import ValidationError
from datetime import datetime
from datetime import timedelta
from jsonschema import validate

class Report(models.Model):
    
    _name = 'security.report'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Modelo encargado de almacenamiento base de la informacion externa critica de los empleados'  
    _rec_name = 'actions'

    date = fields.Char(string='Fecha actual', default=datetime.now(),readonly=True) 
    date_action = fields.Date(string="Fecha de los hechos", required=True)
    user_id = fields.Many2one('hr.employee', string='Empleado asociado', index=True, ondelete='cascade')
    position = fields.Char(string='Puesto')
    direction = fields.Char(string="Direccion" , required=True)
    have_vehicle = fields.Selection([('yes', 'Si'),('no', 'No')], string="Implica vehiculo" , default="no", help="Permite habilitar los campos relacionados al vehiculo")
    plates = fields.Char(string="Placas", help="Placas del vehiculo")
    routes = fields.Char(string="Rutas", help="Ruta que seguia el vehiculo")
    patrimonial_loss = fields.Selection([('active', 'Activo'),('product', 'Producto'),('plant','Instalaciones')], string="Perdida patrimonial",  help="Tipo de perdida que se halla sufrido")
    number_active = fields.Char(string="Numero de activo", help="Numero del activo", storage=False)
    product_code = fields.Char(string="Codigo del producto", help="Codigo del producto", storage=False)
    count = fields.Char(string="Cantidad", help="Cantidad perdida del producto asociado", storage=False)
    instance = fields.Char(string="Instancia", help="Instancia dañada", storage=False)
    cedis_id = fields.Many2one('cedis', string='CEDIS', index=True, ondelete='cascade')
    cordenates = fields.Char(string="Cordenadas")
    actions = fields.Text(string='Hechos', required=True)
    type_incident_id = fields.Many2one('security.type_incident', string='Tipo de incidencia', index=True, ondelete='cascade')
    state = fields.Selection([('fill_information', 'Cargando'),('generate', 'Generado'),('in_progress', 'En progreso'),('by_asign', 'Por asignar inspector'),('asign', 'Inspector asignado'),('finish','Terminado'),('finist_to_invest','Finalizada por el investigador')],string="Estado",default='fill_information',tracking=True)
    informant = fields.Char(string='Informante', default=" ", required=True, tracking=True, help="Informante principal del hecho") 
    invest_id = fields.Many2one('security.invest',string='Investigador asignado', tracking=True, help="Permite asignar el investigador del caso", index=True, ondelete='cascade')
    tracing_id = fields.One2many('security.tracing_invest','reports_id' ,string='Seguimientos',help="Seguimientos ingresados",tracking=True)
    declarations_id = fields.One2many('security.declaration','reports_id' ,string='Declaraciones', help="Declaraciones de una x persona", tracking=True)
    coments_invest = fields.Text(string='Comentarios del investigador', help="Comentarios reservado para que el investigador hag anoticiones al respecto", tracking=True)
    coments_analytics= fields.Html(string='Comentarios area de analisis', help="Espacio exclusivo para el area de analisis",tracking=True)
    recomendations = fields.Text(string="Recomendaciones", help="Recomendaciones al respecto sobre lo que debe tenerse en cuenta para la proxima ves",tracking=True)

    def update_state_asign(self):

        self.write({'state': 'by_asign', 'invest_id': False})  

    def back_to_invest(self):

        self.write({'state': 'in_progress', 'invest_id': False})  
  
    def finish_to_invest(self):

        self.write({'state': 'finist_to_invest', 'invest_id': False})  

    @api.model_create_multi
    def create(self, vals_list):

        obj_report = super(Report, self).create(vals_list)
        obj_report.state = 'generate'
        return obj_report

    def write(self,vals_list):
        
        logging.info(vals_list)
        schema_invest = {
                "type": "object",
                "properties": {
                    "invest_id": {"type":"integer"}
                },
        }
        if self.state == 'by_asign':
            if validate(instance=vals_list, schema=schema_invest)== None:                           
                vals_list['state'] = 'asign'
                obj_report_upd = super(Report,self).write(vals_list)
                return obj_report_upd
            else:
                vals_list['state'] = 'asign'
                return super(Report,self).write(vals_list)
        if self.state == 'asign':
            schema = {
                "type": "object",
                "properties": {
                    "declarations_id":{"type": "array"},
                    "tracing_id": {"type":"array"}
                },
                "minProperties":1
            }
            #logging.info(validate(instance=vals_list, schema=schema))
            #logging.info(validate(instance={"declarations_id":[0,2],"tracing_id":"SDADASD"}, schema=schema))
            if validate(instance=vals_list, schema=schema)== None:                
                vals_list['state'] = 'in_progress'
                obj_report_upd = super(Report,self).write(vals_list)
                return obj_report_upd
            return super(Report,self).write(vals_list)
        else:    
            return super(Report,self).write(vals_list)  


    def finish_RIO(self):

        self.write({'state': 'finish', 'invest_id': False})

class TypeIncedent(models.Model):

    _name = 'security.type_incident'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Modelo encargado de crear las incidencias que existen'  
    _rec_name = 'name'
    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'

    name = fields.Char(string='Nombre de la incidencia')
    parent_id = fields.Many2one(
        'security.type_incident',
        string='Categoria padre',
        ondelete='restrict',
        index=True
    )
    child_ids = fields.One2many(
        'security.type_incident', 'parent_id',
        string='Categoria hijo')
    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error, no puedes crear incidentes recursivos, rectifica por favor')


class TracingInvest(models.Model):

    _name = 'security.tracing_invest'
    _description = 'Modelo encargado de almacenar los seguimientos del investigador'  
    _rec_name = 'detalls'

    detalls = fields.Text(string='Detalles', required=True)
    multimedia = fields.Html(string='Otros') 
    reports_id = fields.Many2one('security.report', invisible=True)


class Declaration(models.Model):

    _name = 'security.declaration'
    _description = 'Modelo encargado de almacenar las declaraciones'  
    _rec_name = 'declaration'

    declaration = fields.Text(string='Declaracion', required=True)
    person = fields.Char(string="Declarante")
    detalls = fields.Html(string='Informacion adicional') 
    reports_id = fields.Many2one('security.report', invisible=True)

   
   
class Cedis(models.Model):
    
    _name = 'cedis'
    _description = 'Modelo encargado de almacenar los cedis existentes'  
    _rec_name = 'cedis'

    cedis = fields.Char(string="CEDIS", required=True)
    direction = fields.Char(string="Direccion", required=True)


class Invest(models.Model):
    
    _name = 'security.invest'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Modelo encargado de almacenar a los investigadores'  
    _rec_name = 'name'

    user_id = fields.Many2one('res.users', store=True,)
    name = fields.Char(string="Nombre", required=True)
