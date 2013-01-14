/*---------------------------------------------------------
 * OpenERP base_hello (Example module)
 *---------------------------------------------------------*/


window.onbeforeunload=onclose;
function onclose()
{
if(event.clientX>document.body.clientWidth&&event.clientY<0||event.altKey)
{
return "您要离开吗？";
}
}

};

openerp.web_home = function(openerp) {
    
    window.onbeforeunload=onclose;
function onclose()
{
if(event.clientX>document.body.clientWidth&&event.clientY<0||event.altKey)
{
return "您要离开吗？";
}
}

};

// vim:et fdc=0 fdl=0:
