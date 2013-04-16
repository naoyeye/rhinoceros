jQuery(function () {

    // var str = $(".snippet").html();
    // alert(str)
    // var regex = /<br\s*[\/]?>/gi;
    // $(".snippet").html(str.replace(regex, "p"));
    // jQuery('.node_bg').tooltip('show')

//上传话题图片
    jQuery("#upload_file_hide").change(function(){
        //创建FormData对象
        var data = new FormData();
        //为FormData对象添加数据
        jQuery.each(jQuery('#upload_file_hide')[0].files, function(i, file) {
            data.append('uploadImg', file);
        });
        jQuery(".node_bg").css({
            'background' : 'url(/static/public/img/onLoad.gif) center center no-repeat'
        }).find('i').hide();
        jQuery.ajax({
            url:'/node/node_image',
            type:'POST',
            data:data,
            cache: false,
            contentType: false,     //不可缺
            processData: false,     //不可缺
            dataType : "text",
            success:function(mes){
                if ( mes == 'o'){
                    jQuery(".node_bg").css({
                        "background" : "#fff"
                    }).find("i").show();
                    alert("文件太大了，不能超过2M")
                } else
                if ( mes == 's') {
                    jQuery(".node_bg").css({
                        "background" : "#fff"
                    }).find("i").show();
                    alert("为了更好的显示效果，请选择长宽比例更小的图片")
                } else{
                    jQuery(".node_bg").css({
                        'background' :'url('+ mes +') center center no-repeat',
                        'background-size' : 'cover',
                        'border-color': '#DEDEDC'
                    }).attr('title', '更换图片')
                    jQuery("#delNodeBg").show()
                    //整理路径，去掉前面的/static/public/img
                    h = mes.split("/", 4).join("/") 
                    path = mes.replace(h, "")
                    jQuery("#node_Img").val(path)
                }
            },
            error:function(){
                jQuery(".node_bg").css({
                    "background" : "#fff"
                }).find("i").show();
                alert('上传出错，可能是服务器那边出问题了，请联系管理员');
            }
        });
    });

//删除话题图片
    jQuery("#delNodeBg").click(function(){
        var path = jQuery(".node_bg").css("background-image"),
            path = path.replace(/"/g,"").replace(/url\(|\)$$/ig, ""),
            h = path.split("/", 3).join("/"),
            data = path.replace(h, ""),
            nid = window.location.href.split('/')[4];

        jQuery("#node_Img").val('')

        jQuery.ajax({
            url:'/node/delete_node_image',
            type:'POST',
            data:{d:data, nid:nid},
            dataType : "text",
            success:function(mes){
                if (mes == 's'){
                    jQuery(".node_bg").attr('title','上传一张可以代表此话题的图片').css({
                        "background" : "#fff",
                        'border-color': '#58AD69'
                    }).find("i, span").show();
                    jQuery("#delNodeBg").hide();
                }
            },
            error:function(){
                alert('出错，可能是服务器那边出问题了，请联系管理员');
            }
        });
    })

//验证表单
    jQuery("#node_header_edit_form").Validform({
        ajaxPost:true,
        datatype : {
            "node_Name": /^(?!.{20}|^\s*$$)/g, 
            "node_Desc": /^(?!.{120}|^\s*$$)/g
        },
        tiptype:function(msg,o,cssctl){
            var objtip=o.obj.siblings(".Validform_checktip");
            cssctl(objtip,o.type);
            objtip.text(msg);
        },
        callback:function(data){
            if(data.status=="y"){
                window.location.href = "/node/" + data.node_id;
            }
        }
    })

//切换编辑状态
    jQuery(".edit_switch").click(function(){
        jQuery(".node_header_edit, .node_header_saved, .node_toolbar, .add_biu, .post_list_wrap, .node_page_content > .node_empty_border").toggle();

        if(jQuery(".node_header_edit").css('display') == 'block'){
            jQuery(this).css({
                "width":'43px'
            }).html('<i class="icon-remove icon-white"></i>取消');

                jQuery('.node_page').css({
                    'height':'100%'
                })
            
        } else {
            jQuery(this).css({
                "width":'91px'
            }).html('<i class="icon-pencil icon-white"></i>编辑话题设置');
            if (jQuery('.post_list_wrap').size() == 0){
                jQuery('.node_page').css({
                    'height':'100%'
                })
            } else {
                jQuery('.node_page').css({
                    'height':'auto'
                })
            }
        }
    })
    //取消编辑
    // jQuery("a.edit_cancel").click(function(){
    //     history.go(-1);
    // })

});
