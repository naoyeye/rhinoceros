/*
 * jQuery File Upload Plugin JS Example 6.7
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */

$(function () {
    'use strict';

    //Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        dropZone: $('#dropzone'),
        change: function () {
            $("#tips").fadeOut();
            $(".fileupload-buttonbar button.start,.fileupload-buttonbar button.cancel").fadeIn();
        },
        dragover: function () {
            $("#tips").fadeOut();
        },
        drop : function(){
            $(".fileupload-buttonbar button.start,.fileupload-buttonbar button.cancel").fadeIn();
        },
        always : function(){
            $(".fileupload-buttonbar button.start,.fileupload-buttonbar button.cancel").hide();
            $(".fileupload-buttonbar button.delete,.fileupload-buttonbar input.toggle").fadeIn();
            $('.form-actions').fadeIn();
        }
    });
    // Enable iframe cross-domain access via redirect option:
    // $('#fileupload').fileupload(
    //     'option',
    //     'redirect',
    //     window.location.href.replace(
    //         /\/[^\/]*$/,
    //         '/cors/result.html?%s'
    //     )
    // );


    //if (window.location.hostname === 'www.2wen.it') {
    if (1 === 1) {
        // Demo settings:
        $('#fileupload').fileupload('option',{
            //url: 'http://localhost:10001/',
            url: 'http://www.yangbodu.com/',
            maxFileSize: 2000000, //2MB
            maxNumberOfFiles: 5,
            //acceptFileTypes: /(\.|\/)(mp3)$/i,
            acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,

            process: [
                {
                    action: 'load',
                    fileTypes: /^image\/(gif|jpeg|png)$/,
                    maxFileSize: 2000000 // 2MB
                },
                {
                    action: 'resize',
                    maxWidth: 1440,
                    maxHeight: 900
                },
                {
                    action: 'save'
                }
            ]        
        });
        // Upload server status check for browsers with CORS support:
        if ($.support.cors) {
            $.ajax({
                //url: 'http://localhost:10001/',
                url: 'http://www.yangbodu.com/',
                type: 'HEAD'
            }).fail(function () {
                $('<span class="alert alert-error"/>')
                    .text('图片服务器出问题了 - ' +
                            new Date())
                    .appendTo('#fileupload');
            });
        }
    } else {
        // Load existing files:
        $('#fileupload').each(function () {
            var that = this;
            $.getJSON(this.action, function (result) {
                if (result && result.length) {
                    $(that).fileupload('option', 'done')
                        .call(that, null, {result: result});
                }
            });
        });
    }

    $("#nextButton").click(function(){
        var rows = $('.table-striped .template-upload').size();
        if(rows > 0) {
            $(this).after('<span class="alert alert-error">似乎还有文件没有上传完？</span>');
            //todo 防止提前提交
        } else {
            var a = new Array(),
                b = new Array();
            $(".template-download .name a").each(function(i) {
                a[i] = $(this).attr('href');
                b[i] = $(this).text();
                $('#path').val(a);
                $('#name').val(b);
            })
        }
        //todo 防止重复提交
    })
});
