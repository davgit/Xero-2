
openerp.xmpp = function(openerp) {
    
    var _t = openerp.web._t;
    var _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    var Groupie = {
            postfix : '@127.0.0.1',
            room : 'test@admin.127.0.0.1',
            connection: null,
            to:null,
            nickname: null,
            NS_MUC: "http://jabber.org/protocol/muc",
            joined: null,
            keeplive: function () {
                Groupie.connection.send($pres().c('priority').t('-1'));
                },
            participants: null,
            on_presence: function (presence) {
                var from = $(presence).attr('from');
                var room = Strophe.getBareJidFromJid(from);
                // make sure this presence is for the right room
                if (room === Groupie.room) {
                    var nick = Strophe.getResourceFromJid(from);
                    if ($(presence).attr('type') === 'error' && !Groupie.joined) {
                        // error joining room; reset app
                        Groupie.connection.disconnect();
                    }
                    else if (!Groupie.participants[nick] && $(presence).attr('type') !== 'unavailable') {
                        // add to participant list
                        Groupie.participants[nick] = true;
                        $('#participant-list').append('<li>' + nick + '</li>');
                        $('#member').append('<div class="chat-friend">' + nick + '</div>');
                        //$('.chat-friend').unbind('click');
                        //$('.chat-friend').bind('click',Groupie.click);
                        if (Groupie.joined) {
                            $(document).trigger('user_joined', nick);
                        }   
                    }
                    else if (Groupie.participants[nick] && $(presence).attr('type') === 'unavailable') {
                        // remove from participants list
                        $('#participant-list li').each(function () {
                            if (nick === $(this).text()) {
                                $(this).remove();
                                return false;
                            }
                        });
                        $('#member div').each(function () {
                            if (nick === $(this).text()) {
                                $(this).remove();
                                return false;
                            }
                        });
                        $(document).trigger('user_left', nick);
                    }
                    if ($(presence).attr('type') !== 'error' && !Groupie.joined) {
                        // check for status 110 to see if it's our own presence
                        if ($(presence).find("status[code='110']").length > 0) {
                            // check if server changed our nick
                            if ($(presence).find("status[code='210']").length > 0) {
                                Groupie.nickname = Strophe.getResourceFromJid(from);
                            }
                        }
                        $(document).trigger("room_joined");
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
                    var delayed = $(message).children("delay").length > 0 || $(message).children("x[xmlns='jabber:x:delay']").length > 0;
                    if (!notice) {
                        var delay_css = delayed ? " delayed": "";
                        var action = body.match(/\/me (.*)$/);
                        if (!action) {
                            $('#content').append('<p>'+body+'</p>');
                            Groupie.add_message("<div class='message" + delay_css + "'>" +
                                                "&lt;<span class='" + nick_class + "'>" +
                                                nick + "</span>&gt; <span class='body'>" +
                                                body + "</span></div>");
                        }
                        else {
                            Groupie.add_message("<div class='message action " + delay_css + "'>" +
                                                "* " + nick + " " + action[1] + "</div>");
                            $('#content').append('<p>'+body+'</p>');
                            
                        }
                    }
                    else {
                        $('#content').append('<p>'+body+'</p>');
                        Groupie.add_message("<div class='notice'>*** " + body + "</div>");
                    }
                };
                return true;
            },
            on_private_message: function (message) {
                var from = $(message).attr('from');
                var room = Strophe.getBareJidFromJid(from);
                var nick = Strophe.getResourceFromJid(from);
                // make sure this message is from the correct room
                if (room === Groupie.room) {
                    var body = $(message).children('body').text();
                    Groupie.add_message("<div class='message private'>" +
                                        "@@ &lt;<span class='nick'>" +
                                        nick + "</span>&gt; <span class='body'>" +
                                        body + "</span> @@</div>");
                }
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
                Groupie.connection.send($pres({to: Groupie.room + "/" + Groupie.nickname,type: "unavailable"}));
               Groupie.connection.disconnect();
            });
            $('#input').keypress( function (ev) {
                if (ev.which === 13) {
                    ev.preventDefault();
                    var body = $(this).val();
                    console.log(body);
                    var match = body.match(/^\/(.*?)(?: (.*))?$/);
                    var args = null;
                    if (match) {
                        if (match[1] === "msg") {
                            args = match[2].match(/^(.*?) (.*)$/);
                            if (Groupie.participants[args[1]]) {
                                Groupie.connection.send($msg({to: Groupie.room + "/" + args[1],type: "chat"}).c('body').t(body));
                                Groupie.add_message("<div class='message private'>" +
                                                    "@@ &lt;<span class='nick self'>" +
                                                    Groupie.nickname + "</span>&gt; <span class='body'>" +
                                                    args[2] + "</span> @@</div>");}
                            else {Groupie.add_message("<div class='notice error'>" + "Error: User not in room." +"</div>");}
                        }
                        else if (match[1] === "me" || match[1] === "action") {
                            Groupie.connection.send($msg({to: Groupie.room,type: "groupchat"})
                                                    .c('body').t('/me ' + match[2]));
                        }
                        else if (match[1] === "topic") {
                            Groupie.connection.send($msg({to: Groupie.room,type: "groupchat"}).c('subject').t(match[2]));
                        }
                        else if (match[1] === "kick"){Groupie.connection.sendIQ($iq({to: Groupie.room,type: "set"})
                                                    .c('query', {xmlns: Groupie.NS_MUC + "#admin"})
                                                    .c('item', {nick: match[2],role: "none"}));
                        }
                        else if (match[1] === "ban") {Groupie.connection.sendIQ($iq({to: Groupie.room,type: "set"})
                                                    .c('query', {xmlns: Groupie.NS_MUC + "#admin"})
                                                    .c('item', {jid: Groupie.participants[match[2]],affiliation: "outcast"}));
                        }
                        else {
                            Groupie.add_message("<div class='notice error'>" +
                                                "Error: Command not recognized." + "</div>");
                        }
                    }
                    else {
                        Groupie.connection.send(
                        $msg({to: Groupie.room,type: "groupchat"}).c('body').t(body));
                    }
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
                        $("#chatroom").removeClass("chatroomloading")
                        $('#ember224').removeClass("unavailable");
                        $(document).trigger('connected');
                    }
                    else if (status === Strophe.Status.DISCONNECTED) {
                        $(document).trigger('disconnected');
                    }
                    else if (status === Strophe.Status.CONNECTING) {
                        $("#chatroom").addClass('chatroomloading')                       
                    }
                });
            });
        
    $(document).bind('connected', function () {
        Groupie.joined = false;
        Groupie.participants = {};
        Groupie.connection.send($pres().c('priority').t('-1'));
        Groupie.connection.addHandler(Groupie.on_presence,null,"presence");
        Groupie.connection.addHandler(Groupie.on_public_message,null,"message","groupchat");
        Groupie.connection.addHandler(Groupie.on_private_message,null,"message","chat");
        Groupie.connection.send($pres({to: Groupie.room + "/" + Groupie.nickname}).c('x', {xmlns: Groupie.NS_MUC}));
        $(".msgblank").removeClass("hidden")
        //setInterval(Groupie.keeplive,5000);
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
        $('#chat').append("<div class='notice'>*** Room joined.</div>");
        $('#msg').append("<div class='notice'>*** Room joined.</div>")
    });
    
    $(document).bind('user_joined', function (ev, nick) {
        Groupie.add_message("<div class='notice'>*** " + nick + " joined.</div>");
    });
   
    $(document).bind('user_left', function (ev, nick) {
        
        Groupie.add_message("<div class='notice'>*** " + nick + " left.</div>");
    });
    
    //extend
    
    openerp.web.Header.include({
    
        start: function() {
            
            this._super();
            //extend

            $("#oe_header").append("<div id='ember224' class='ember-view chat-dock-wrapper clearfix unavailable'>\
                                            <div id='ember229' class='ember-view chat-tab-list clearfix'></div>\
                                            <div id='ember233' class='ember-view roster chat-tab'>\
                                                <a id='ember236' class='ember-view chat-button'>\
                                                    <div class='chat-button-rule'>\
                                                        <div class='image-block clearfix'>\
                                                            <img class='image-block-image icon' src='/web/static/src/img/empty.gif' width='1' height='1'>\
                                                            <b id = 'chatroom' class='chatroom'>聊天室</b>\
                                                        </div>\
                                                    </div>\
                                                </a>\
                                            </div>\
                                        </div>\
            ");
            
            //
            $("#ember224").before('\
                                  <div class="chat-dock-wrapper chatroster">\
                                  <div>Chat</div>\
                                  <hr/>\
                                  <div id = "member">\
                                  </div>\
                                  </div>\
            ');
            
            
            
            //Chat
            $("#oe_header").before('<div class="msgblank hidden"><div id="content"></div><input id="msg" class="inputin"/><button id="send" type="button">Send</button></div>');
            
            
            $("#send").click(function () {body = $("#msg").val();Groupie.connection.send($msg({to: Groupie.room,type: "groupchat"}).c('body').t(body));});
            
            
            Groupie.click = function () {
                Groupie.to = this.innerHTML;
                
                Groupie.connection.send($msg({to: Groupie.room,type: "groupchat"}).c('body').t(body));
            };
            
            //Login
            //Groupie.nickname = openerp.connection.username;
            //$(document).trigger('connect', {
            //    jid:'admin@127.0.0.1',
            //    password: 'admin'
            $("#chatroom").click( function(){
                Groupie.nickname = openerp.connection.username;
                $(document).trigger('connect', {
                    jid:'admin@127.0.0.1',
                    password: 'admin'
                });
                
                });
            //});
            
            //end
        },
    
    })
    
    //end
}





