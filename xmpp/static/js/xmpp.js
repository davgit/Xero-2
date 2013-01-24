
openerp.xmpp = function(openerp) {
    
    var _t = openerp.web._t;
    var _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    var Groupie = {
            connection: null,
            room: null,
            nickname: null,
            NS_MUC: "http://jabber.org/protocol/muc",
            joined: null,
            participants: null,
            on_presence: function (presence) {
                var from = $(presence).attr('from');
                var room = Strophe.getBareJidFromJid(from);
                // make sure this presence is for the right room
                if (room === Groupie.room) {
                        var nick = Strophe.getResourceFromJid(from);
                    if ($(presence).attr('type') === 'error' && !Groupie.joined) {
                        // error joining room; reset app
                        Groupie.connection.disconnect();}
                    else if (!Groupie.participants[nick] && $(presence).attr('type') !== 'unavailable')
                    {   // add to participant list
                        Groupie.participants[nick] = true;
                        $('#participant-list').append('<li>' + nick + '</li>');}
                    if ($(presence).attr('type') !== 'error' && !Groupie.joined) {
                        // check for status 110 to see if it's our own presence
                        if ($(presence).find("status[code='110']").length > 0) {
                            // check if server changed our nick
                            if ($(presence).find("status[code='210']").length > 0) {
                            Groupie.nickname = Strophe.getResourceFromJid(from);}
                            // room join complete
                            $(document).trigger("room_joined");
                        }
                    }
                }
                return true;
            },
            on_public_message: function (message) {
                var from = $(message).attr('from');
                var room = Strophe.getBareJidFromJid(from);
                var nick = Strophe.getResourceFromJid(from);
                // make sure message is from the right place
                if (room === Groupie.room) {
                    // is message from a user or the room itself?
                    var notice = !nick;
                    // messages from ourself will be styled differently
                    var nick_class = "nick";
                    if (nick === Groupie.nickname) {
                        nick_class += " self";
                    }
                    var body = $(message).children('body').text();
                    if (!notice) {
                        Groupie.add_message("<div class='message'>" +
                                            "&lt;<span class='" + nick_class + "'>" +
                                            nick + "</span>&gt; <span class='body'>" +
                                            body + "</span></div>");}
                    else {
                        Groupie.add_message("<div class='notice'>*** " + body + "</div>");
                    };
                };
                return true;
            },
            add_message: function (msg) {
                // detect if we are scrolled all the way down
                var chat = $('#chat').get(0);
                var at_bottom = chat.scrollTop >= chat.scrollHeight - chat.clientHeight;
                $('#chat').append(msg);
                // if we were at the bottom, keep us at the bottom
                if (at_bottom) {
                    chat.scrollTop = chat.scrollHeight;
                }
            },
            rawInput:function (data)
            {
                console.log('RECV: ' + data);
            },
            rawOutput:function (data)
            {
                 console.log('SENT: ' + data);
            },
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
            $('#leave').click(function () {
                Groupie.connection.send(
                $pres({to: Groupie.room + "/" + Groupie.nickname,type: "unavailable"}));
                Groupie.connection.disconnect();
            });
            $('#input').keypress(function (ev) {
                if (ev.which === 13) {
                ev.preventDefault();
                var body = $(this).val();
                Groupie.connection.send(
                $msg({
                to: Groupie.room,
                type: "groupchat"}).c('body').t(body));
                $(this).val('');
                }
                });
            self.login();
        },
        login:function () {
            
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
            Groupie.connection.rawInput = Groupie.rawInput;
            Groupie.connection.rawOutput = Groupie.rawOutput;
            Groupie.connection.connect(data.jid, data.password,
                function (status) {
                    if (status === Strophe.Status.CONNECTED) {
                        $(document).trigger('connected');}
                    else if (status === Strophe.Status.DISCONNECTED) {
                        $(document).trigger('disconnected');
                    }
                });
            });
        
    $(document).bind('connected', function () {
        Groupie.joined = false;
        Groupie.participants = {};
        Groupie.connection.send($pres().c('priority').t('-1'));
        Groupie.connection.addHandler(Groupie.on_presence,null, "presence");
        Groupie.connection.addHandler(Groupie.on_public_message,null, "message", "groupchat");
        Groupie.connection.send($pres({to: Groupie.room + "/" + Groupie.nickname}).c('x', {xmlns: Groupie.NS_MUC}));
    });
            
    $(document).bind('disconnected', function () {
        Groupie.connection = null;
        $('#participant-list').empty();
        $('#room-name').empty();
        $('#room-topic').empty();
        $('#chat').empty();
        $('#login_dialog').dialog('open');
    });
    
    $(document).bind('room_joined', function () {
        Groupie.joined = true;
        $('#leave').removeAttr('disabled');
        $('#room-name').text(Groupie.room);
        $('#chat').append("<div class='notice'>*** Room joined.</div>")
    });

}

