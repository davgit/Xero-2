openerp.web_home = function(openerp) {

    var on_logout = this.sessions.session0.connection.session_logout;
    var rpc = this.sessions.session0.connection.rpc;
    var end_date = new Date();
    user_context  = this.sessions.session0.connection.user_context
    //console.log(this.sessions.session0.connection.rpc);
    // window.onunload = onbeforeunload_handler;
    console.log(openerp);
    openerp.web.Connection.include({
        init: function() {
        this._super();
        this.server = null;
        this.debug = ($.deparam($.param.querystring()).debug != undefined);
        // TODO: session store in cookie should be optional
        this.name = openerp._session_id;
        this.qweb_mutex = new $.Mutex();
        var end_date = new Date();
        var obj = this;
        console.log(this);
        $(window).bind('beforeunload', function (e) {
            if (true) {
                    return 'You have unsaved changes';}
                });},
        })
};

// vim:et fdc=0 fdl=0:
