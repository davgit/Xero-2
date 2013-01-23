
openerp.xmpp = function(openerp) {
    var _t = openerp.web._t;
    var _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    var Groupie = {
              connection: null,
              room: null,
              nickname: null
    };
    openerp.web.client_actions.add('xmpp.ui', 'openerp.xmpp.HomePage');
    openerp.xmpp.HomePage = openerp.web.View.extend({
        template: 'xmpp',
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
            $('.secondary_menu').hide();
            self.group();
        },
        group:function () {
            
            $('#login_dialog').dialog({
                autoOpen: true,
                draggable: false,
                modal: true,
                title: 'Join a Room',
                buttons: {
                    "Join": function () {
                        Groupie.room = $('#room').val();
                        Groupie.nickname = $('#nickname').val();
                        $(document).trigger('connect', {
                            jid: $('#jid').val(),
                            password: $('#password').val()
                        });
                        $('#password').val('');
                        $(this).dialog('close');
                    }
                }
            });
        }
    });
    //extend
    $(document).bind('connect', function (ev, data) {
                Groupie.connection = new Strophe.Connection("http://127.0.0.1:7070/http-bind/");
                console.log(data);
                console.log(Groupie.connection);
                console.log(Strophe.Status);
                Groupie.connection.connect(
                    data.jid, data.password,
                    function (status) {
                        console.log(status);
                        if (status === Strophe.Status.CONNECTED) {
                            $(document).trigger('xmppconnected');}
                        else if (status === Strophe.Status.DISCONNECTED) {
                            $(document).trigger('xmppdisconnected');
                        }
                    });
            });
        
            $(document).bind('xmppconnected', function () {
            // nothing here yet
                    alert('123');
            });
            
            $(document).bind('xmppdisconnected', function () {
            // nothing here yet
            alert('111111');
            });
}

