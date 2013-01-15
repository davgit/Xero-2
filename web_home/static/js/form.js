function fnsubmit(){
        
        var notebox=$('#living-effect');
        console.log(notebox);
        alert(notebox.val());
        if(notebox.val() =="")
	{
		alert("请填写留言内容！");
		return;
	}
    };