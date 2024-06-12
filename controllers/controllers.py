# -*- coding: utf-8 -*-
# from odoo import http


# class CarClickup(http.Controller):
#     @http.route('/car_clickup/car_clickup', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/car_clickup/car_clickup/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('car_clickup.listing', {
#             'root': '/car_clickup/car_clickup',
#             'objects': http.request.env['car_clickup.car_clickup'].search([]),
#         })

#     @http.route('/car_clickup/car_clickup/objects/<model("car_clickup.car_clickup"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('car_clickup.object', {
#             'object': obj
#         })
