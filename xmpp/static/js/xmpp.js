
openerp.xmpp = function(openerp) {
    var _t = openerp.web._t;
    var _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    openerp.web.client_actions.add('xmpp.ui', 'openerp.xmpp.HomePage');
    openerp.xmpp.HomePage = openerp.web.OldWidget.extend({
        init: function (parent) {
            this._super(parent);
            this.user = _.extend(new openerp.web.DataSet(this, 'res.users'), {
                index: 0,
                name: [this.session.username]
            });
        },
        start: function () {
            this._super();
            var self = this;
            },
        render: function() {
                return qweb_template("xmpp")();
            }
    });
    //
    
}

