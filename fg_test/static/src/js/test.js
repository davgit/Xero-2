
//
openerp.fg_test = function(openerp)  {
    var _t = openerp.web._t,
    _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    openerp.web.HtmlView.include({
    on_loaded: function(data) {
        var self = this;
        if (data) {
            this.fields_order = [];
            this.fields_view = data;
            var frame = new (this.registry.get_object('frame'))(this, this.fields_view.arch);

            this.rendered = QWeb.render(this.form_template, { 'frame': frame, 'widget': this });
        }
        this.$element.html(this.rendered);
        _.each(this.widgets, function(w) {
            w.start();
        });
        this.$form_header = this.$element.find('.oe_form_header:first');
        this.$form_header.find('div.oe_form_pager button[data-pager-action]').click(function() {
            var action = $(this).data('pager-action');
            self.on_pager_action(action);
        });

        this.$form_header.find('button.oe_form_button_save').click(this.on_button_save);
        this.$form_header.find('button.oe_form_button_cancel').click(this.on_button_cancel);

        this.has_been_loaded.resolve();
        $('.secondary_menu').hide();
        $('.oe-view-manager-header').hide();
        //extend
        forkit();
        $('#t').click(function(){
            $('#t').toggleClass('imgstyle','test')
            })
    },
        });
    }
    
