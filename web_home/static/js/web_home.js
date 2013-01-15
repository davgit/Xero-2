


openerp.web_home = function(openerp) {
    var _t = openerp.web._t,
    _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    openerp.web.client_actions.add( 'homepage.overview', 'openerp.web_dashboard.HomePage');
    openerp.web_dashboard.HomePage = openerp.web.View.extend({
    template: 'Homepage',
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
        console.log(this.user);
        this.$element.html(QWeb.render('Homepage.content', {
            user: this.user,
        }));

    },
    
});
    //
    
};


