odoo.define('pos_multi_currency.screen', function (require) {
var PaymentScreen = require('point_of_sale.PaymentScreen');
var core = require('web.core');
const NumberBuffer = require('point_of_sale.NumberBuffer');
const Registries = require('point_of_sale.Registries');
var QWeb = core.qweb;

// PaymentScreen.extend({
// //     click_paymentmethods: function (){
// //         this._super.apply(this, arguments);
// //         this.$('.currency-buttons').empty();
// //         var $currency_buttons = $(QWeb.render('PyamentCurrecy', {widget: this}));
// //         $currency_buttons.appendTo(this.$('.currency-buttons'));
// //     }
        // addNewPaymentLine({ detail: paymentMethod }) {
        //     // original function: click_paymentmethods
        //     let result = this.currentOrder.add_paymentline(paymentMethod);
        //     console.log('addNewPaymentLine');
        //     console.log(result);
        //     console.log(this.currentOrder);
        //     if (result){
        //         NumberBuffer.reset();
        //         return true;
        //     }
        //     else{
        //         this.showPopup('ErrorPopup', {
        //             title: this.env._t('Error'),
        //             body: this.env._t('There is already an electronic payment in progress.'),
        //         });
        //         return false;
        //     }
        // }

// });

    const PaymentScreen1 = PaymentScreen => class extends PaymentScreen {
        addNewPaymentLine({ detail: paymentMethod }) {
            // original function: click_paymentmethods

            console.log('addNewPaymentLine');
            // add_paymentline 
            var paymentlines = this.currentOrder.get_paymentlines();
            var is_multi_currency = false;
            _.each(paymentlines, function (line) {
                if (line.payment_method.currency_id[0] !== paymentMethod.currency_id[0]) {
                    is_multi_currency = true;
                }
            });
            if (is_multi_currency) {
                this.showPopup('ErrorPopup', {
                    title : this.env._t("Payment Error"),
                    body  : this.env._t("Payment of order should be in same currency. Payment could not be done with two different currency"),
                });
                return false;
            } else {
                var journal_currency_id = paymentMethod.currency_id[0];
                if (this.currentOrder.currency.id !== journal_currency_id) {
                    var currency = _.findWhere(this.env.pos.multi_currencies, {id:journal_currency_id})
                    if (currency){
                        this.currentOrder.set_currency(currency);
                    }
                }
            
                // add_paymentline

                let result = this.currentOrder.add_paymentline(paymentMethod);
                // var $currency_buttons = $(QWeb.render('PyamentCurrecy', {widget: this}));
                if (result){
                    NumberBuffer.reset();
                }
                else{
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Error'),
                        body: this.env._t('There is already an electronic payment in progress.'),
                    });
                }
            }

            $('.currency-buttons').empty();
            var $currency_buttons = $(QWeb.render('PyamentCurrecy', {env: this.env}));
            $currency_buttons.appendTo($('.currency-buttons'));
        }
    };

    Registries.Component.extend(PaymentScreen, PaymentScreen1);

    return PaymentScreen;

});


