openerp.web_home = function(openerp) {
   
   
    openerp.web.WebClient.include({
    on_logout: function() {
        var self = this;
        this.session.session_logout().then(function () {
            $(window).unbind('hashchange', self.on_hashchange);
            self.do_push_state({});
            //would be cool to be able to do this, but I think it will make addons do strange things
            //this.show_login();
            window.location.reload();
        });
    },
    });
    
    var on_logout = openerp.webclient.on_logout;
    console.log(openerp.web.WebClient.on_logout);
    function onbeforeunload_handler(){  
        var warning="确认退出?";          
        return warning;  
    }  
    window.onbeforeunload = onbeforeunload_handler;
    
    
};

// vim:et fdc=0 fdl=0:
