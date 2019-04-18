$(window).resize(function(e) {
    $("#bd").height($(window).height() - $("#hd").height() - $("#ft").height()-6);
	$(".wrap").height($("#bd").height()-6);
	$(".nav").css("minHeight", $(".sidebar").height() - $(".sidebar-header").height()-1);
	$("#iframe").height($(window).height() - $("#hd").height() - $("#ft").height()-12);
}).resize();
$('.exitDialog').Dialog({
	title:'提示信息',
	autoOpen: false,
	width:400,
	height:200

});
$('.exit').click(function(){
	$('.exitDialog').Dialog('open');
});

$('.exitDialog input[type=button]').click(function(e) {
    $('.exitDialog').Dialog('close');

	if($(this).hasClass('ok')){
		window.location.href = "login.html"	;
	}
});
$(function() {
	$('.nav>li').click(function () {
		$('.nav>li').removeClass("current");
		$(".subnav li a").removeClass("color");
		$(this).addClass("current");
		var $ul = $(".subnav",this);
		$(".subnav").slideUp();
		if ($ul.is(':visible')) {
			$ul.slideUp();
			//$(".subnav li a").removeClass("color");
		}else {
			$ul.slideDown();
		}
	});
	$(".subnav li").click(function(e){
		$(".subnav li a").removeClass("color");
		$("a",$(this)).addClass("color");
		e.stopPropagation();

	});
	//$(".nav").click(function(){
    //
	//})
});
//modify
$().ready(function() {
	$("#modifypwdbtn").click(function() {
		$("#modifydiv").show();
		$("#oldpwdtext").val('');
		$("#newpwd").val('');
		$("#newpwd2").val('');
	});

	$("#oldpwdtext").blur(function() {
		if ($("#oldpwdtext").val() != "")
			$("#oldpwdtexttip").css("color", "green");
		else
			$("#oldpwdtexttip").css("color", "red");

	});
	$("#newpwd").blur(function() {

		if ($("#newpwd").val() != "")
			$("#newpwdtip").css("color", "green");
		else
			$("#newpwdtip").css("color", "red");
	});
	$("#newpwd2").blur(function() {

		if ($("#newpwd2").val() != "")
			$("#newpwd2tip").css("color", "green");
		else
			$("#newpwd2tip").css("color", "red");
	});

	$("#modifypwdbtna").click(function() {
		var oldpwd = $("#oldpwdtext").val();
		var newpwd = $("#newpwd").val();
		var newpwd2 = $("#newpwd2").val();
		if (oldpwd.length < 6) {
			$("#oldpwdtext").focus();
			humane.error("请输入原始密码");
		} else if (newpwd.length < 6) {

			$("#newpwd").focus();
			humane.error("密码长度不能小于6");
		} else if (newpwd2.length < 6) {

			$("#newpwd2").focus();
			humane.error("密码长度不能小于6");
		} else if (newpwd != newpwd2) {

			humane.error("两次密码不相同");
		} else {
			// 提交到服务器
			$.post("modifypwd", {
				'oldpwd':oldpwd,
				'newpwd':newpwd
			}, function(result) {//alert(result.length);
				// "success",failed				
				if (result == 'success') {
					humane.success("修改密码成功 ！");
					$("#modifydiv").hide();
				}else
					humane.error("修改密码失败 ！");
			}, 'html');
		}

	});
	$("#modifypwdcancel").click(function() {

		$("#modifydiv").hide();
		$("#oldpwdtext").val('');
		$("#newpwd").val('');
		$("#newpwd2").val('');
	});

});