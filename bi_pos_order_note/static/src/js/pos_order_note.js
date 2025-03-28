//console.log('Order Note load')
odoo.define('bi_pos_order_note.pos', function(require){
	'use strict';

	var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    //var Model = require('web.DataModel');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var time = require('web.time');
    var utils = require('web.utils');
    var _t = core._t;


    models.load_models({
        model: 'pos.order.line',
        fields: ['notes_product_line'],
        domain: null,
        loaded: function(self, pos_order_line) {
            
            self.pos_order_line = pos_order_line;
        },
    });



    models.load_models({
        model: 'pos.order',
        fields: ['pos_ordernote'],
        domain: function(self){ return [['session_id', '=', self.pos_session.name],['state', 'not in', ['draft', 'cancel']]]; },
        loaded: function(self, pos_order) {
            self.pos_order = pos_order;
        },
    });

  
              




/*var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            
            
            var product_model = _.find(this.models, function(model) {
                return model.model === 'pos.order.line';
            });
            product_model.fields.push('notes_product_line');
            
            return _super_posmodel.initialize.call(this, session, attributes);
        },
            push_order: function(order, opts) {
                    opts = opts || {};
                    var self = this;

                    if(order){
                        this.db.add_order(order.export_as_JSON(pos_ordernote: ));
                    }

                    var pushed = new $.Deferred();

                    this.flush_mutex.exec(function(){
                        var flushed = self._flush_orders(self.db.get_orders(), opts);

                        flushed.always(function(ids){
                            pushed.resolve();
                        });

                        return flushed;
                    });
                    return pushed;
                },
            });

*/

   


   	// Start PosNoteWidget
	
    var PosNoteWidget = screens.ActionButtonWidget.extend({
        template: 'PosNoteWidget',

        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        renderElement: function(){
	    var self = this;
	    this._super();
	    }, 

        button_click: function() {
            var self = this;
            var order = self.pos.get('selectedOrder');
            var orderlines = order.orderlines;
            if (orderlines.length === 0) {
                self.gui.show_popup('error', {
                    'title': _t('Empty Order'),
                    'body': _t('There must be at least one product in your order before Add a note.'),
                });
                return;
            }
            else{
                self.gui.show_popup('pos_note_popup_widget', {});

            }
        },
        
    });

   


    screens.define_action_button({
        'name': 'Pos Note Widget',
        'widget': PosNoteWidget,
        'condition': function() {
            return true;
        },
    });

    



    // PosNotePopupWidget Popup start

    var PosOrderNotePopupWidget = popups.extend({
        template: 'PosOrderNotePopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        

	    renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var selectedOrder = self.pos.get('selectedOrder');



            this.$('#apply_note').click(function() {
                var entered_note = $("#entered_note").val();
                console.log("oooooooooooooooooooooooooooooooooooooo",entered_note)
                var partner_id = false
                if (order.get_client() != null)
                    partner_id = order.get_client();
                var product_id = false
                if (order.get_selected_orderline().product.id != null)
                    product_id = order.get_selected_orderline().product.id

                    var orderlines = order.orderlines;
                    
                   var selectedOrderLine = order.get_selected_orderline()

		   selectedOrderLine.set_staystr(entered_note);

            });


        },

    });
    gui.define_popup({
        name: 'pos_note_popup_widget',
        widget: PosOrderNotePopupWidget
    });

    // End Popup start




        // exports.Orderline = Backbone.Model.extend ...
    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
		initialize: function(attr,options){
		OrderlineSuper.prototype.initialize.apply(this, arguments);
        this.pos   = options.pos;
        this.order = options.order;
        
        if (options.json) {
            this.init_from_JSON(options.json);
            return;
        }

        this.set_staystr();

    },
    clone: function(){
        var orderline = new exports.Orderline({},{
            pos: this.pos,
            order: null,
            product: this.product,
            price: this.price,
        });
        
        orderline.quantity = this.quantity;
        orderline.quantityStr = this.quantityStr;
        orderline.stayStr = this.stayStr;
        orderline.discount = this.discount;
        orderline.type = this.type;
        orderline.selected = false;
        return orderline;
    },
    
    set_staystr: function(entered_note){
    
	  this.stayStr = entered_note;
	  this.trigger('change',this);
    },

    get_to_stay: function(){
        return this.stayStr;
    },

    export_as_JSON: function() {
        var pack_lot_ids = [];
        if (this.has_product_lot){
            this.pack_lot_lines.each(_.bind( function(item) {
                return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
            }, this));
        }
        return {
            qty: this.get_quantity(),
            price_unit: this.get_unit_price(),
            price_subtotal: this.get_price_without_tax(),
            price_subtotal_incl: this.get_price_with_tax(),
            discount: this.get_discount(),
            product_id: this.get_product().id,
            tax_ids: [[6, false, _.map(this.get_applicable_taxes(), function(tax){ return tax.id; })]],
            id: this.id,
            pack_lot_ids: pack_lot_ids,
	    notes_product_line: this.get_to_stay()

        };
    },

    
    
    });
    // End Orderline start

	// screens.PaymentScreenWidget.include({
	//    show: function(){
	// 	    var self = this;
	// 	    this._super();
		    
	// 	    this.pos.get_order().clean_empty_paymentlines();
	// 	    this.reset_input();
	// 	    this.render_paymentlines();
	// 	    this.order_changes();
		    
		    
	// 	    $('#pos_ordernote').on('focus', function() {
 //                window.document.body.removeEventListener('keypress', self.keyboard_handler);
 //                window.document.body.removeEventListener('keydown', self.keyboard_keydown_handler);
 //            });
 //            $('#pos_ordernote').on('focusout', function() {
 //                window.document.body.addEventListener('keypress', self.keyboard_handler);
 //                window.document.body.addEventListener('keydown', self.keyboard_keydown_handler);
 //            });
            
	// 	    window.document.body.addEventListener('keypress',this.keyboard_handler);
	// 	    window.document.body.addEventListener('keydown',this.keyboard_keydown_handler);
	// 	},
 //    });






        // exports.Orderline = Backbone.Model.extend ...
    var OrderSuper = models.Order;
    models.Order = models.Order.extend({


    	get_pos_ordernote: function() {
            //console.log("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAyaz") 
	    var pos_ordernote = $("#pos_ordernote").val();
            //console.log("pos_ordernoteeeeeeeeeeeeeeeeeeeeeee_pos_ordernote", pos_ordernote);
	    return pos_ordernote;
        },
        
        export_as_JSON: function() {
            var self = this;
            //this.pos_ordernote = self.get_pos_ordernote();
            var loaded = OrderSuper.prototype.export_as_JSON.call(this);
	    //console.log("loadedddddddddddddddddddddddddddddddddddddddddd",loaded)
            loaded.pos_ordernote = self.get_pos_ordernote();
		//console.log("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm", loaded.pos_ordernote)
            return loaded;
        },
        
        /*
        export_as_JSON: function() {
        var orderLines, paymentLines;
        orderLines = [];
        this.orderlines.each(_.bind( function(item) {
            return orderLines.push([0, 0, item.export_as_JSON()]);
        }, this));
        paymentLines = [];
        this.paymentlines.each(_.bind( function(item) {
            return paymentLines.push([0, 0, item.export_as_JSON()]);
        }, this));
        return {
            name: this.get_name(),
            amount_paid: this.get_total_paid(),
            amount_total: this.get_total_with_tax(),
            amount_tax: this.get_total_tax(),
            amount_return: this.get_change(),
            lines: orderLines,
            statement_ids: paymentLines,
            pos_session_id: this.pos_session_id,
            pricelist_id: this.pricelist ? this.pricelist.id : false,
            partner_id: this.get_client() ? this.get_client().id : false,
            user_id: this.pos.get_cashier().id,
            uid: this.uid,
            sequence_number: this.sequence_number,
            creation_date: this.validation_date || this.creation_date, // todo: rename creation_date in master
            fiscal_position_id: this.fiscal_position ? this.fiscal_position.id : false
            pos_ordernote: self.get_pos_ordernote()
        };*/
   

    
    
    });
    // End Orderline start


});
