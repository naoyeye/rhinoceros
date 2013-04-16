
//设置超时时间为10秒钟 //自动关闭fancybox
var timeout = 10;
function show() {
    var showbox = jQuery("#init_value");
    showbox.html(timeout);
    timeout--;
    if (timeout == 0) {
        window.opener = null;
        jQuery.fancybox.close()

    }
    else {
        setTimeout('show()', 1000);
    }
}

jQuery(function () {

// 弹出申请表单窗口
    jQuery('#applyForRights').click(function(){
        var loginBox = jQuery('#apply_box')
        jQuery.fancybox( loginBox ,{minHeight : 10, minWidth : 400, padding: 0});
    })

// 验证申请表单
    jQuery("#apply_box_form").Validform({
        ajaxPost:true,
        tiptype:function(msg,o,cssctl){
            var objtip=o.obj.siblings(".Validform_checktip");
            cssctl(objtip,o.type);
            objtip.text(msg);
        },
        callback:function(data){
            if(data.status=="y"){
                jQuery('#apply_box_form').remove()
                jQuery('#apply_box_inner').append('<p style="margin:0;padding:90px 10px 10px 10px;background:url(/static/public/img/post_image_upload/done.png) center 0 no-repeat;font-size:14px;">' + data.info + '<br/><br/><span style="font-size:12px">我们会尽快处理，处理结果将会发送到你之前填写的邮箱地址。<br/>如果没有收到，请查看是否在垃圾箱中</span></p><div id="timeClose"><span id="init_value">10</span>秒后自动关闭</div>');
                show(); //定时10秒自动关闭fancybox
                jQuery('span.remove').remove();
                jQuery('a.remove').append('<a href="javascript:void(0)" class="btn pull-right">审核中...请等待邮件通知</a>').remove();
                
            }
        }
    })

});