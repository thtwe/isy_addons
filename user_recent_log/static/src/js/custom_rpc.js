//odoo.define('user_recent_log.CustomBasicModel', function (require) {

// var BasicModel = require('@web/model/model');
// var rpc = require('web.rpc'); 
// var Changes = false;

// var CustomBasicModel = BasicModel.extend({

//     _fetchRecord: function (record, options) {
//         var _super = this._super.bind(this);
//         var changes = window.Changes;
//         window.Changes = false;
//         rpc.query({
//                     model: 'user.recent.log',
//                     method: 'get_recent_log',
//                     args: [record.model, record.res_id, changes],
//                 });
//         return _super(record, options);
//     },

//     _generateChanges: function (record, options) {
//         var _super = this._super.bind(this);
//         var res = _super(record, options);
//         window.Changes = res
//         return res
//     },
// })

// return CustomBasicModel;

//});
