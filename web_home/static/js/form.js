function fnsubmit(){
        
        var notebox = $('#living-effect');
	var username = $('#username');
        
	if (notebox.val() ==""){return;};
	
	if(notebox.val() != "")
        {
		$('#homepagebox')[0].innerHTML += "<div><p>" +
		notebox.val()+"</p>"+'<p style="text-align:right">'+
		username.text()+"<p style='float:right'>"+Date()+"</p>"+"</p>"+"</div>"
		notebox.val('');
	};
    };
$(document).keypress(
	function(e){
if(e.ctrlKey && e.which == 13 || e.which == 10 || e.which == 13) { 
$("#btn").click();
e.preventDefault();
$("#living-effect").val("");
} 
});