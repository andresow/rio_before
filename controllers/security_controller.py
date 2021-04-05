from odoo import http
from odoo.http import request
from openerp.addons.website.controllers.main import Website

class RIO(http.Controller):

    @http.route('/website/RIO.webform', type="http", auth="public", website=True)
    def rio_form(self, **kwargs):
        return http.request.render('RIO.create_rio', {})
    
    @http.route('/create/rio_form', type="http", auth="public", website=True)
    def create_rio(self, **kwargs):
        request.env['security.report'].sudo().create(kwargs)
        return request.render("RIO.report_thanks")

class CustomWebsite(http.Controller):

    @http.route('/website/RIO.custom_web_test', type="http" , auth="public",website=True)
    def custom_process(self, **kwargs):
        return http.request.render('RIO.index_custom')