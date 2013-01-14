openerp.web_home = function(openerp) {

    var on_logout = this.sessions.session0.connection.session_logout;
    var rpc = this.sessions.session0.connection.rpc;
    var end_date = new Date();
    user_context  = this.sessions.session0.connection.user_context
    //console.log(this.sessions.session0.connection.rpc);
    // window.onunload = onbeforeunload_handler;

};

// vim:et fdc=0 fdl=0:
