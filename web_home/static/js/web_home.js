


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
            ids: [this.session.uid]
        });
        this.dataset = new openerp.web.DataSetSearch(this, 'ir.actions.todo');
    },
    start: function () {
        this._super();
        var self = this;
        return this.user.read_index(['groups_id']).pipe(function(record) {
            var todos_filter = [
                ['type', '!=', 'automatic'],
                '|', ['groups_id', '=', false],
                     ['groups_id', 'in', record['groups_id']]];
            return $.when(
                self.dataset.read_slice(
                    ['state', 'action_id', 'category_id'],
                    { domain: todos_filter }
                ),
                self.dataset.call('progress').pipe(
                        function (arg) { return arg; }, null))
        }, null).then(this.on_records_loaded);

    },
    on_records_loaded: function (records, progress) {
        var grouped_todos = _(records).chain()
            .map(function (record) {
                return {
                    id: record.id,
                    name: record.action_id[1],
                    done: record.state !== 'open',
                    to_do: record.state === 'open',
                    category: record['category_id'][1] || _t("Uncategorized")
                }
            })
            .groupBy(function (record) {return record.category})
            .value();
        this.$element.html(QWeb.render('Homepage.content', {
            completion: 100 * progress.done / progress.total,
            groups: grouped_todos,
            task_title: _t("Execute task \"%s\""),
            checkbox_title: _t("Mark this task as done"),
            _: _
        }));
        var $progress = this.$element.find('div.oe-config-progress-bar');
        $progress.progressbar({value: $progress.data('completion')});

        var self = this;
        this.$element.find('dl')
            .delegate('input', 'click', function (e) {
                // switch todo status
                e.stopImmediatePropagation();
                var new_state = this.checked ? 'done' : 'open',
                      todo_id = parseInt($(this).val(), 10);
                self.dataset.write(todo_id, {state: new_state}, {}, function () {
                    self.start();
                });
            })
            .delegate('li:not(.oe-done)', 'click', function () {
                self.widget_parent.widget_parent.widget_parent.do_execute_action({
                        type: 'object',
                        name: 'action_launch'
                    }, self.dataset,
                    $(this).data('id'), function () {
                        // after action popup closed, refresh configuration
                        // thingie
                        self.start();
                    });
            });
    }
});
    //
    
};


