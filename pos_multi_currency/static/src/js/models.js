odoo.define('pos_multi_currency.models', function (require) {
var core = require('web.core');

var models = require('point_of_sale.models');
// var PosBaseWidget = require('point_of_sale.BaseWidget');
var _t = core._t;

models.load_models({
    model: 'res.currency',
    fields: ['name','symbol','position','rounding','rate'],
    loaded: function (self, currencies) {
        self.multi_currencies = currencies;
    }
});

models.load_models({
    model:  'pos.payment.method',
    fields: ['name', 'is_cash_count', 'use_payment_terminal','journal_id','currency_id'],
    domain: function(self, tmp) {
        return [['id', 'in', tmp.payment_method_ids]];
    },
    loaded: function(self, payment_methods) {
        self.payment_methods = payment_methods.sort(function(a,b){
            // prefer cash payment_method to be first in the list
            if (a.is_cash_count && !b.is_cash_count) {
                return -1;
            } else if (!a.is_cash_count && b.is_cash_count) {
                return 1;
            } else {
                return a.id - b.id;
            }
        });
        self.payment_methods_by_id = {};
        _.each(self.payment_methods, function(payment_method) {
            self.payment_methods_by_id[payment_method.id] = payment_method;

            var PaymentInterface = self.electronic_payment_interfaces[payment_method.use_payment_terminal];
            if (PaymentInterface) {
                payment_method.payment_terminal = new PaymentInterface(self, payment_method);
            }
        });
    }
});

var _super_Order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function () {
        _super_Order.initialize.apply(this, arguments);
        this.currency = this.pos.currency;
    },
    init_from_JSON: function (json) {
        _super_Order.init_from_JSON.apply(this, arguments);
        this.currency = json.currency;
    },
    export_as_JSON: function () {
        var values = _super_Order.export_as_JSON.apply(this, arguments);
        values.currency = this.currency;
        return values;

    },
    set_currency: function (currency) {
        if (this.currency.id === currency.id) {
            return;
        }
        var form_currency = this.currency || this.pos.currency;
        var to_currency = currency;
        this.orderlines.each(function (line) {
            line.set_currency_price(form_currency, to_currency);
        });
        this.currency = currency;
    },
    get_currency: function (){
        return this.currency;
    },

    format_currency: function(amount, precision) {
        console.log('ISY format_currency')
        var currency =
            this && this.currency
                ? this.currency
                : { symbol: '$', position: 'after', rounding: 0.01, decimals: 2 };

        amount = this.format_currency_no_symbol(amount, precision, currency);

        if (currency.position === 'after') {
            return amount + ' ' + (currency.symbol || '');
        } else {
            return (currency.symbol || '') + ' ' + amount;
        }
    },

    // add_paymentline: function (payment_method) {
    //     console.log('ISY add_paymentline');
    //     var paymentlines = this.get_paymentlines();
    //     var is_multi_currency = false;
    //     _.each(paymentlines, function (line) {
    //         if (line.payment_method.currency_id[0] !== payment_method.currency_id[0]) {
    //             is_multi_currency = true;
    //         }
    //     });
    //     if (is_multi_currency) {
    //         this.pos.gui.show_popup('alert', {
    //             title : _t("Payment Error"),
    //             body  : _t("Payment of order should be in same currency. Payment could not be done with two different currency"),
    //         });
    //     } else {
    //         var journal_currency_id = payment_method.currency_id[0];
    //         if (this.currency.id !== journal_currency_id) {
    //             var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
    //             if (currency){
    //                 this.set_currency(currency);
    //             }
    //         }
    //         _super_Order.add_paymentline.apply(this, arguments);
    //     }
    // },
});

models.Orderline = models.Orderline.extend({
    set_currency_price: function (form_currency, to_currency){
        var conversion_rate =  to_currency.rate / form_currency.rate;
        this.price = this.price * conversion_rate;
    },
});

models.PosModel = models.PosModel.extend({
    format_currency: function(amount, precision) {
        var currency =
            this && this.currency
                ? this.currency
                : { symbol: '$', position: 'after', rounding: 0.01, decimals: 2 };

        amount = this.format_currency_no_symbol(amount, precision, currency);

        currency = this.get_order().currency || currency;
        if (currency.position === 'after') {
            return amount + ' ' + (currency.symbol || '');
        } else {
            return (currency.symbol || '') + ' ' + amount;
        }
    },
})


// PosBaseWidget.include({
//     format_currency: function (amount,precision){
//         var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
//         amount = this.format_currency_no_symbol(amount, precision);
//         currency = this.pos.get_order().currency || currency;
//         if (currency.position === 'after') {
//             return amount + ' ' + (currency.symbol || '');
//         } else {
//             return (currency.symbol || '') + ' ' + amount;
//         }
//     },
// });


});
