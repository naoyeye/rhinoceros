$(function () {

    //找回密码
    $("#forgotButton").click(function(){
        if($("#forgotWrap").is(':visible')){
            $("#landingMain").animate({
                top: 0 
            },350)
            $("#formWrap, #loginWrap").hide()
            //$("#landingForm").attr("action","")
            $("#buttonGroup a").removeClass('active')
        } else {
            $("#loginWrap").hide()
            $("#forgotWrap").fadeIn()
            $("#buttonGroup a").removeClass('active')
        }
    })

    //手绘验证码
    $('#landingForm').motionCaptcha({
        errorMsg: '不标准哦，再试一下吧',
        successMsg: '画的不错！通过了！',
        noCanvasMsg: "你的浏览器不支持 <canvas> - 试试Chrome, FF4, Safari 或者 IE9."

    });

    //switch
    $("#reg_link").click(function(){
        if($("#regWrap").is(':visible')){
            $("#landingMain").animate({
                top: 0 
            },350)
            $("#landingContent h2, #landingContent h3").fadeIn()
            //$("#landingForm").attr("action","")
            $("#formWrap, #regWrap").hide()
            $("#buttonGroup a").removeClass('active')
        } else {
            $("#landingMain").animate({
                top: -300 
            },350)
            $("#landingContent h2, #landingContent h3").fadeOut()
            //$("#landingForm").attr("action","")
            setTimeout(function() {
                  $("#formWrap, #regWrap").fadeIn()
            }, 400);
            
            $("#loginWrap, #forgotWrap").hide()
            $("#buttonGroup a").removeClass('active')
            $(this).addClass('active')
        }
    })

    $("#login_link").click(function(){
        if($("#loginWrap").is(':visible')){
            $("#landingMain").animate({
                top: 0 
            },350)
            $("#formWrap, #loginWrap").hide()
            //$("#landingForm").attr("action","")
            $("#buttonGroup a").removeClass('active')
        } else {
            $("#landingMain").animate({
                top: -80 
            },350)
            $("#landingContent h2, #landingContent h3").fadeIn()
            //$("#landingForm").attr("action","/account/landing_login")
            setTimeout(function() {
                  $("#formWrap, #loginWrap").fadeIn()
            }, 400);
            $("#regWrap, #forgotWrap").hide()
            $("#buttonGroup a").removeClass('active')
            $(this).addClass('active')
        }
    })

    //tip
    $("#buttonGroup a").hover(function(){
        $("#buttonGroup a span").hide();
        $(this).find('span').show()
    },function(){
        $(this).find('span').hide()
    })

    // $("#regForm").Validform({
    //     btnSubmit      : "#regButton",
    //     tiptype        : 2,
    //     tipSweep       : false,
    //     showAllError   : false,
    //     postonce       : true,
    //     datatype       : {
    //         "*6-10": /^[^\s]{6,10}$/,
    //         "regUserName": /^[\u4E00-\u9FA5\uf900-\ufa2d]{2,8}$/
    //     },
    //     beforeCheck:function(curform){
    //         alert(1);
    //     },
    // })
    
    //注册
    $("#landingForm").Validform({
        datatype       : {
            "regUserName": /^[a-zA-Z]{1}[\w\-]{1,15}$/
        },

        tiptype:function(msg,o,cssctl){
            //msg：提示信息;
            //o:{obj:*,type:*,curform:*}, obj指向的是当前验证的表单元素（或表单对象），type指示提示的状态，值为1、2、3、4， 1：正在检测/提交数据，2：通过验证，3：验证失败，4：提示ignore状态, curform为当前form对象;
            //cssctl:内置的提示信息样式控制函数，该函数需传入两个参数：显示提示信息的对象 和 当前提示的状态（既形参o中的type）;
            if(!o.obj.is("form")){//验证表单元素时o.obj为该表单元素，全部验证通过提交表单时o.obj为该表单对象;
                var objtip=o.obj.siblings(".Validform_checktip");
                cssctl(objtip,o.type);
                objtip.text(msg);
            }else{
                var objtip=o.obj.find("#msgdemo");
                cssctl(objtip,o.type);
                objtip.text(msg);
            }
        },
        usePlugin:{
            passwordstrength:{
                minLen:6,//设置密码长度最小值，默认为0;
                maxLen:16,//设置密码长度最大值，默认为30;
                trigger:function(obj,error){
                    //该表单元素的keyup和blur事件会触发该函数的执行;
                    //obj:当前表单元素jquery对象;
                    //error:所设密码是否符合验证要求，验证不能通过error为true，验证通过则为false;
                    
                    //console.log(error);
                    if(error){
                        obj.siblings(".Validform_checktip").css({'display':'inline-block'});
                        obj.siblings(".passwordStrength").hide();
                    }else{
                        obj.siblings(".Validform_checktip").hide();
                        obj.siblings(".passwordStrength").show();   
                    }
                }
            }
        }
    });

    // var demo = $("#landingForm2").Validform();
    // $("#loginButton").click(function(){
    //     demo.ajaxPost();
    //     return false;
    // });
    
    //登录
    $("#landingForm2").Validform({
        ajaxPost:true,

        // tiptype:function(msg,o,cssctl){
        //     //msg：提示信息;
        //     //o:{obj:*,type:*,curform:*}, obj指向的是当前验证的表单元素（或表单对象），type指示提示的状态，值为1、2、3、4， 1：正在检测/提交数据，2：通过验证，3：验证失败，4：提示ignore状态, curform为当前form对象;
        //     //cssctl:内置的提示信息样式控制函数，该函数需传入两个参数：显示提示信息的对象 和 当前提示的状态（既形参o中的type）;
        //     if(!o.obj.is("form")){//验证表单元素时o.obj为该表单元素，全部验证通过提交表单时o.obj为该表单对象;
        //         var objtip=o.obj.siblings(".Validform_checktip");
        //         cssctl(objtip,o.type);
        //         objtip.text(msg);
        //     }else{
        //         var objtip=o.obj.find("#msgdemo");
        //         cssctl(objtip,o.type);
        //         objtip.text(msg);
        //     }
        // },

        tiptype:function(msg,o,cssctl){
            var objtip=$("#msgdemo2");
            cssctl(objtip,o.type);
            objtip.text(msg);
        },

        callback:function(data){
            if(data.status=="y"){
                //setTimeout(function(){
                    //$.Hidemsg(); //公用方法关闭信息提示框;显示方法是$.Showmsg("message goes here.");
                    //$.Showmsg("成功");
                    window.location.href = "/";
                //},1000);
            }
        }
    })
    
    //找回密码
    $("#landingForm3").Validform({
        ajaxPost:true,
        tiptype:function(msg,o,cssctl){
            var objtip=$("#msgdemo3");
            cssctl(objtip,o.type);
            objtip.text(msg);
        },
        callback:function(data){
            if(data.status=="y"){
                //setTimeout(function(){
                    //$.Hidemsg(); //公用方法关闭信息提示框;显示方法是$.Showmsg("message goes here.");
                    // $.Showmsg("成功");
                    //alert(1)
                    //window.location.href = "/";
                //},1000);
            }
        }
    })
})