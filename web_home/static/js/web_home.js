
openerp.web_home = function(openerp) {
    var _t = openerp.web._t;
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
        this.$element.html(QWeb.render('Homepage.content', {
            user: this.user,
        }));
        $('#btn').click( function (){
                        
                        if ($('#living-effect').val() ==""){return;};
                        
                        if($('#living-effect').val() != "")
                        {
                            var note = $('#living-effect').val();
                            
                            self.rpc('/web/dataset/create', {
                                            model: 'notebook',
                                            data: {name:self.uid,note:note},
                                        });
                            
                            self.rpc('/web/listview/load', {
                                            model: 'notebook',
                                            view_id: 200,
                                            view_type: "tree",
                                        });
                            
                            self.rpc('/web/dataset/search_read', {
                                            model: 'notebook',
                                            fields: ['name','date','note'],
                                            limit: 80});
                            
                            $('#living-effect').val('');
                                
                        };});},});
    //
    openerp.web.ListView.include({
    start: function() {
        var self = this;
        this._super();
        this.$element.addClass('oe-listview');
        if (self.model == 'notebook'){
            console.log(self.model);
            $('#btn').click(function(){
            var obj = self;
            obj.reload_content();})
            };
        return this.reload_view(null, null, true);
},});
};

