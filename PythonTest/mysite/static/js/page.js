function first(num){
	$("[name=pageNo]").val(1);
	$("form").submit();
}

function prev(num){
	if(num<=1){
		alert("已经是第一页");
	}else{
		num--;
	}
	$("[name=pageNo]").val(num);
	$("form").submit();
}

function next(num){
	var totalPage = $("[name=totalPage]").val();
	if(num>=totalPage){
		alert("已经是末页");
	}else{
		num++;
	}
	$("[name=pageNo]").val(num);
	$("form").submit();
}

function last(num){
	$("[name=pageNo]").val(num);
	$("form").submit();
}

