jQuery(function(){
    //页面滚动
    jQuery(window).scroll(function() {
        //导航和回顶部的显隐
        var t = jQuery(window).scrollTop();
        if(t >= 50){
            // alert(1)
            jQuery('.edit_switch, .add_biu, .avatar20').hide();
            // if(jQuery('#rec_nav').size() == 0){ //判断是不是首页
            //     jQuery('#creatNewNode').css({
            //         'right' : 10
            //     })
            // }
            jQuery('#creatNewNode').hide()
            jQuery('.post_node_link').removeClass('active');
        }
        if(t >= 1024){
            // alert(2)
            jQuery('#goTop').removeClass('invisible')
        }
        if( t == 0){
            // alert(3)
            jQuery('.avatar20').fadeIn(100)
            // if(jQuery('#rec_nav').size() == 0){ //判断是不是首页
            //     jQuery('#creatNewNode').css({
            //         'right' : 60
            //     })
            // }
            jQuery('#creatNewNode').show()
            jQuery('.edit_switch, .add_biu').fadeIn(100).css({
                'display' : 'inline-block'
            });
            jQuery('.post_node_link').addClass('active');
        }
        if (t < 1024){
            // alert(4)
            jQuery('#goTop').addClass('invisible')
        }
    })

    // 回顶端 
    jQuery('#goTop').click(function(){
        jQuery(document).stop().scrollTo(0, 400);
    })

    // note: 暂时屏蔽个人主页
    // jQuery('a[href*=member]').live('click',OpenOverlay)

    // 弹出overlay层
    function OpenOverlay(){
        var douban_id = jQuery(this).attr('href').split('/')[2],
            douban_uid = jQuery(this).attr('title')
        jQuery('body').addClass('home-overlay-enabled');
        jQuery('.overlay_username').html(douban_uid);
        jQuery('#overlay_douban_link').attr('href', 'http://www.douban.com/people/' + douban_id)
        return false;
    }

    // 关闭overlay层
    jQuery('.home-overlay-close ').click(function(){
        jQuery('body').removeClass('feedback-overlay-enabled').removeClass('home-overlay-enabled');
    })

    //打开feedback层
    jQuery('#feedbackBtn').TWITTER_tooltip({
        placement : 'right'
    }).click(openFeedback)

    function openFeedback(){
        jQuery('#feedback_wrap h3').remove();
        jQuery('body').addClass('feedback-overlay-enabled');
        jQuery('#feedbackForm input:submit').removeClass('disabled').removeAttr('disabled');
        jQuery('#feedbackForm').fadeIn();
    }

    function closeFeedback(){
        jQuery('#feedbackForm').hide().after('<h3>提交成功，感谢你的反馈 :) <span class="show" style="font-size:12px;font-weight:normal">本窗口会自动关闭</span></h3>');
        jQuery('#feedbackForm textarea').val('');
        jQuery('#feedbackForm input:submit').addClass('disabled').attr('disabled','disabled');
        setTimeout(function(){
            jQuery('body').removeClass('feedback-overlay-enabled');
        },3000)
    }

    //feedback 表单验证
    jQuery('#feedbackForm').Validform({
        tipSweep : true,
        ajaxPost:true,
        datatype : {
            "feedback_content": /^[\w\W]{1,500}$$/
        },
        tiptype:function(msg,o,cssctl){
            var objtip=o.obj.siblings(".Validform_checktip");
            cssctl(objtip,o.type);
            objtip.text(msg);
        },
        beforeSubmit:function(curform){
            jQuery('#feedback_wrap .btn').val('发布中...').removeClass('btn-primary');
        },
        callback:function(data){
            if(data.status=="y"){
                closeFeedback();
            }
        }
    })


    //查看提醒
    jQuery('#notification_num, #close_ntf_block').click(checkNotification)

    function checkNotification(){
        
        if(jQuery('#notification_list').css('display') == 'none'){
            var h = jQuery(window).height(), //获得窗口高度
                t = jQuery(document).scrollTop(); //获得滚动条位置
            jQuery.cookie('s_t_v', t, { expires: 7, path: '/'}); //把位置存到cookie中
            jQuery('#main').height(0).hide().css({'overflow': 'hidden'}); //隐藏滚动条
            jQuery('#notification_list').css({
                'max-height' : h - 330 // 显示adsss
            }).slideDown(200); //显示提醒层
            jQuery('#arts').show();
            jQuery('#notification_wrap').height(h).css({
                'background':'#333332'
            })
            
        } else {
            var top = jQuery.cookie('s_t_v'); //得到之前的滚动条位置 
            jQuery('#main').height('100%').show().css({'overflow': 'visible'}); //恢复页面高度和滚动条
            jQuery('#notification_list').slideUp(150); //隐藏提醒层
            jQuery('#arts').hide();
            jQuery('#notification_wrap').height(0).css({
                'background':'none'
            })
            jQuery(document).scrollTop(top) //重新设置滚动条位置，回到刚才浏览的地方
            jQuery.cookie('s_t_v', null); //清除cookie
        }
    }

    //提醒滚动条
    jQuery("#notification_list").niceScroll({
        touchbehavior:false,
        cursorcolor:"#777",
        cursoropacitymax:0.8,
        cursorwidth:8,
        background:"none",
        cursorborder:"none",
        autohidemode:false,
        boxzoom:false,
        railalign: "right"
    });

    //点击某条提醒后，将该提醒设为已读
    jQuery('#notification_wrap a.ntf_link_to').click(function(){

        var t = jQuery(this),
            id = t.attr('id').split('_')[1],
            href = t.attr('href'),
            host = window.location.host,
            url = window.location.href,
            url = url.replace(host,'').replace('http://','');

        jQuery.ajax({
            url:'/notification/make_read',
            type:'POST',
            data:{ id : id},
            dataType : "json",
            success:function(mes){
                if (mes.status == 'y'){
                    var num = Number(jQuery('#notification_num span').html()),
                        newnum = num - 1;
                    jQuery('#notification_num span').html(newnum);
                    if(href == url){
                        t.parents('li').eq(0).remove();
                        checkNotification();
                        if(jQuery('#notification_num span').text() == '0'){
                            jQuery('#notification').remove();
                        }
                    }
                    location.href= href;
                }
            }
        });
        return false;
    })

    //全部标记为已读
    jQuery('#make_all_read_button').click(function(){
        var list = new Array();
        jQuery('#notification_list .ntf_link_to').each(function(i){
            list[i] = jQuery(this).attr('id').split('_')[1];
            // list.push('list=' + $(this).attr('id').split('_')[1])
        })

        // id_list = '['+ id_list + ']'
        // alert(list.join(","))
        // return false;

        jQuery.ajax({
            url:'/notification/make_all_read',
            type:'POST',
            data:{ 'id_list' : list.toString()},
            dataType : "text",
            success:function(mes){
                if (mes == 's'){
                    jQuery('#notification span').html(0);
                    jQuery('#notification').slideUp(250);
                    setTimeout(function(){
                        checkNotification();
                    },450)
                    setTimeout(function(){
                        jQuery('#notification_wrap').remove()
                    },650)
                }
            }
        });
    })

    //toggle profile desc
    jQuery('#more_desc').toggle(
        function(){
            jQuery(this).attr('title', '隐藏简介');
            jQuery(this).find('i').addClass('icon-chevron-up').removeClass('icon-chevron-down');
            if(jQuery('#desc_full').css('display') == 'none'){
                // jQuery('#desc_s').hide();
                jQuery('#desc_full').slideDown(150);
            }
        },
        function(){
            jQuery(this).attr('title', '查看简介');
            jQuery(this).find('i').addClass('icon-chevron-down').removeClass('icon-chevron-up');
            if(jQuery('#desc_full').css('display') == 'block'){
                // jQuery('#desc_s').show();
                jQuery('#desc_full').slideUp(150);
            }
        }
    )

    //change profile background image
    jQuery('#change_background_img_btn').toggle(
        function(){
            jQuery(this).html('取消更改');
            if(jQuery('#change_background_img_form').css('display') == 'none'){
                jQuery('#change_background_img_form').fadeIn(200);
            }
        },
        function(){
            jQuery(this).html('更改背景图片');
            if(jQuery('#change_background_img_form').css('display') == 'block'){
                jQuery('#change_background_img_form').fadeOut(200);
            }
        }
    )

    //未登录时保存跳转连接到cookie
    jQuery('#goLoginBtn a').click(function(){
        var url =  window.location.href;
        $.cookie('redirect_url', url, { expires: 7, path: '/'});
        // window.location.href = '/';
    })
    
})

// 过滤转义字符
function toTxt(str){
    var RexStr = /\<|\>|\"|\'|\&/g;
    str = str.replace(RexStr,
        function(MatchStr){
            switch(MatchStr){
                case "<":
                    return "&lt;";
                    break;
                case ">":
                    return "&gt;";
                    break;
                case "\"":
                    return "&quot;";
                    break;
                case "'":
                    return "&#39;";
                    break;
                case "&":
                    return "&amp;";
                    break;
                default :
                    break;
            }
        }
    )
    return str;
}


