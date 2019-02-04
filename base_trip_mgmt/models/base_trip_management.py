# -*- coding: utf-8 -*-.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import defaultdict
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

class BaseSDTrip(models.Model):
    _name = "base.sd.trip"
    _description = "SD Trip"
    _inherit = ["mail.thread"]
    _rec_name = "vehicle_num"

    Processes = [("draft", "Draft"),
                ("planned", "Planned"),
                ("loaded", "Loaded"),
                ("inprogress", "In Progress"),
                ("done", "Done"),
                ("cancelled", "Cancelled")]

    # attributes
    vehicle_num = fields.Char(string="Vehicle No.")
    driver_name = fields.Char(string="Driver Name")
    scheduled_date = fields.Date("Scheduled Date")
    state = fields.Selection(Processes, string="State", default='loaded')

    # relations
    vehicle_id = fields.Many2one("fleet.vehicle","Vehicle")
    model_id = fields.Many2one("fleet.vehicle.model","Model")
    stock_ids = fields.One2many("base.trip.stock.details","base_trip_stock_id",string="Stock Details")
    trip_ids = fields.One2many("base.trip","base_sd_trip_trip_id",string="Vehicle trip")
    check_plan_click = fields.Boolean(string="Check Plan Click")
    check_update_click = fields.Boolean(string="Check Update Click")

    @api.multi
    def create_trip_stock(self, status=None):
        base_shop_stock_obj = self.stock_ids
        for obj in base_shop_stock_obj:
            obj.unlink()
        base_route_stock_detail = self.trip_ids
        base_shop_stock_detail = []
        product_from_route = [] 
        product_for_stock = [] 
        for obj in base_route_stock_detail:
            for key in obj.shop_stock_details_ids:
                base_shop_stock_detail.append(key)
        for temp in base_shop_stock_detail:
            temp_dict_for_route_product = {'product_id':temp.product_id.id,'required_qty':temp.required_qty,'delivered_qty':temp.delivered_qty}
            product_from_route.append(temp_dict_for_route_product)
        # print('product_from_route',product_from_route)
        product_id_list = []  
        for product in product_from_route:
            product_id_list.append(product['product_id'])
        product_id_list = list(set(product_id_list))
        for product in product_id_list:
            req_qty=0.0
            del_qty=0.0
            for product_route in product_from_route:
                if int(product_route['product_id']) == product:
                    req_qty += float(product_route['required_qty'])
                    del_qty += float(product_route['delivered_qty'])
            temp_dict_for_stock_product = {'product_id':product, 'required_qty': req_qty, 'delivered_qty':del_qty}
            product_for_stock.append(temp_dict_for_stock_product)
        for obj in product_for_stock:
            base_shop_stock_obj.create({
                'product_id': int(obj['product_id']),
                'required_stock': obj['required_qty'],
                'delivered_stock': obj['delivered_qty'],
                'base_trip_stock_id':self.id
            })
        self.check_plan_click = True
        if status == 'update':
            self.check_update_click = False
        
    @api.multi
    def update_trip_stock(self):
        if self.check_update_click == True:
            self.create_trip_stock('update')
       

    @api.multi
    def write(self, write_vals):
        if 'trip_ids' in write_vals:
            self.check_update_click = True
        return super(BaseSDTrip, self).write(write_vals)

    @api.model
    def data_for_live_traking(self, id=None):
        # print('*******************************', id)
        sd_trips_loaded = self.search([('state', 'in', ['loaded'])])
        final_data_dic, final_data_list, planned_trip_dic, planned_trip_list = {}, [], {}, []
        loaded_trip_dic = {}
        loaded_trip_list = []
        loaded_trip_dic["status"] = "Loaded"
        for sd_trip in sd_trips_loaded:
            loaded_qty = required_qty = 0
            for stock in sd_trip.stock_ids:
                loaded_qty += stock.loaded_stock
                required_qty += stock.required_stock
            trip_dic = {}
            trip_dic["id"] = sd_trip.id
            trip_dic["name"] = sd_trip.vehicle_num
            trip_dic_extra = {}
            trip_dic_extra["model"] = sd_trip.model_id.name
            trip_dic_extra["reg_no"] = sd_trip.vehicle_num
            trip_dic_extra["loaded_qty"] = loaded_qty
            trip_dic_extra["required_qty"] = required_qty
            trip_dic_extra["cap"] = sd_trip.model_id.vehicle_capacity
            trip_dic["vehicle"] = trip_dic_extra
            loaded_trip_list.append(trip_dic)
        loaded_trip_dic["trips"] =  loaded_trip_list
        loaded_trip_dic['driver_data'] = [{'name':'Rohit Pandey'},{'name':'Pawnesh Sir'},{'name':'Rahul Sir'},{'name':'Krishna Sir'},{'name':'Rohin Sir'}]
        loaded_trip_dic['vechile_data'] = [{'number':'7777'},{'number':'8888'},{'number':'9999'},{'number':'0000'},{'number':'7777'},{'number':'8888'},{'number':'9999'},{'number':'0000'}]
        # print('--------loaded_trip_dic-----------', loaded_trip_list)
        trip = None
        if id:
            # print('----------id["id"]-------------', id, type(id), id['id'], type(id['id']))
            for pr_trip in loaded_trip_list:
                # print('-----------------trip---------------', trip['id'], type(trip['id']))
                if pr_trip['id'] == int(id['id']):
                    trip = pr_trip
        # print('----------trip----------', trip)
        return {'loaded_trip_dic':loaded_trip_dic, 'trip':trip}

    @api.model
    def filter_trip_data(self, vals):
        # print('------------vals------------', vals)
        check = all(value == '' for value in vals.values())
        # print('---------------------------', check)

        # if 'scheduled_date' in vals and vals.get('scheduled_date'):
        #     date = datetime.strptime(vals['scheduled_date'], '%m/%d/%Y')
        #     print('-------------vals-----------', vals['scheduled_date'])
        # if 'scheduled_date' in vals and vals.get('scheduled_date'):
        # records = self.sudo().search(['|','|','|', ('scheduled_date', '=', vals['scheduled_date']), ('driver_name', '=', vals['driver_name']), ('id', '=', vals['trip_name']),('vehicle_num', '=', vals['vehicle_num'])])
        # print('----------------records------------------------', records)
        result = None
        if not check:
            query = "SELECT * from base_sd_trip WHERE "
            
            data_tuple = ()
            if 'scheduled_date' in vals and vals.get('scheduled_date'):
                print('-------vals["scheduled_date"]------', vals['scheduled_date'])
                from_date, to_date = vals['scheduled_date'].split('-')
                from_term = ('scheduled_date', datetime.strptime(from_date.strip(), '%m/%d/%Y').strftime('%Y-%m-%d'))
                to_term = ('scheduled_date', datetime.strptime(to_date.strip(), '%m/%d/%Y').strftime('%Y-%m-%d'))
                print('from_term',from_term[0], from_term[1],'to_term',to_term[0],to_term[1])
                query += '('
                query += from_term[0]
                query += ' >= '
                query += "'" + from_term[1] + "'"
                query += ' AND '
                query += to_term[0]
                query += ' < '
                query += "'" + to_term[1] + "'"
                query += ')'

                # print('---------------query------------',query)


            if 'driver_name' in vals and vals.get('driver_name'):
                term = ('driver_name', vals['driver_name'])
                data_tuple += term
            if 'trip_name' in vals and vals.get('trip_name'):
                term = ('id', vals['trip_name'])
                data_tuple += term
            if 'vehicle_num' in vals and vals.get('vehicle_num'):
                term = ('vehicle_num', vals['vehicle_num'])
                data_tuple += term

            # print('**************************************', data_tuple)


            # print('------------len(data_tuple)--------------', len(data_tuple))
            
            for term in range(0, len(data_tuple), 2):
                # print(data_tuple[term], data_tuple[term+1], '*******************')
                # print('-----------------------', term)
                if ('scheduled_date' in vals and vals.get('scheduled_date') and term ==0 ) or (term > 0):
                    query += ' OR '
                query += '('
                query += data_tuple[term]
                query += ' = '
                query += "'" + data_tuple[term+1] + "'"
                query += ')'

            # query = query[:len(query)-4]

            query += ';'

            # print('----------------query----------------', query)            

            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
            # print('--------------res------------------------', result)
            # print('--------------res------------------------', len(result))
        return result



class Basetrip(models.Model):
    _name = "base.trip"
    _description = "Base Trip" 
    _inherit = ["mail.thread"]
    _rec_name = "sequence"

    Processes = [("planned", "Planned"),                
                ("inprogress", "In Progress"),                             
                ("completed", "Completed"),
                ("cancelled", "Cancelled")]

    # attributes
    sequence = fields.Integer("Sequence")
    state = fields.Selection(Processes, string="State", default='planned')

    # relations
    shop_id = fields.Many2one("res.partner",string="Shop")
    stock_location_id = fields.Many2one(related="shop_id.agent_location_id",string='Stock Location')
    shop_stock_details_ids = fields.One2many("base.shop.stock.details","base_shop_stock_id",string="Stock Details")
    base_sd_trip_trip_id = fields.Many2one('base.sd.trip') 


class BaseShopStockDetails(models.Model):
    _name = "base.shop.stock.details"
    _description = "Base Shop Stock Details"
    _inherit = ["mail.thread"]
    _rec_name = "product_id"

    # attributes
    product_id = fields.Many2one("product.product","Product")    
    required_qty = fields.Float('Required Qty')
    delivered_qty = fields.Float('Delivered Qty')

    # relations
    base_shop_stock_id = fields.Many2one('base.trip')

class BaseTripStockDetails(models.Model):
    _name = "base.trip.stock.details"
    _description = "Base Trip Stock Details"
    _inherit = ["mail.thread"]
    _rec_name = "product_id"

    # attributes
    product_id = fields.Many2one("product.product","Product")    
    loaded_stock = fields.Float("Loaded Stock")
    required_stock = fields.Float('Required Stock')
    delivered_stock = fields.Float('Delivered Stock')

    # relations
    base_trip_stock_id = fields.Many2one('base.sd.trip')




