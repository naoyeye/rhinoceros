$(function(){
    $('#landingForm').Validform({
        
        tipSweep : false,
        beforeSubmit: function(curform){
            $('.why').hide()
            curform.find('.input-append').hide().after('<div style="background: url(/static/public/img/onLoad.gif) no-repeat scroll top center transparent;height:40px;padding-top:30px">...请稍候...</div>')
        },
        tiptype:function(msg,o,cssctl){

            var objtip=o.obj.siblings(".Validform_checktip");
            cssctl(objtip,o.type);
            objtip.text(msg);

        }
    })
})