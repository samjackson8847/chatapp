
$(window).ready(function() {
    var cookieValue = $.cookie("api_key");
    var pusher = new Pusher('a8355dbe7a6a0daf08a4');
    $('<div id="wrap" class="chat_button_div" style="display:none;"><div class="chat-box"><input type="checkbox" /><label data-expanded="Minimize Chatbox" id="chat_name_label" data-collapsed=""></label><div class="chat-box-content"><div class="chat-panel panel panel-success"><div class="tab-content"><div id="offline" class="tab-pane active"><form class="form-signin chat_form_submit"><p class="text-muted text-center btn-block btn btn-primary btn-rect">Please Fill Details To Contact</p><input type="text" placeholder="Name" class="form-control" name="name" /><input type="email" placeholder="Your E-mail" name="email" class="form-control" /><textarea type="text" name="description" class="form-control"></textarea><input id="id_name" value="'+user_key+'" type="hidden" name="key" /><input class="btn text-muted text-center btn-success button_submit" type="submit" value ="Contact Me"/></form></div></div></div></div></div></div><div id="wrap" class="chat_div_popup" style="display:none;"><i class="icon-large icon-remove-sign close_button"></i><div class="chat-box"><input type="checkbox" class="checkbox_button" /><label data-expanded="Minimize Chatbox" data-collapsed="Open Chatbox"></label><div class="chat-box-content"><div class="chat-panel panel panel-success"><div class="panel-heading"><i class="icon-comments"></i></div><div class="panel-body"><ul class="chat chat_append_message"></ul></div><div class="panel-footer"><p class="visitor_type" style="display:none;"></p><div class="input-group"><form class="visitor_form_chat"><input id="btn-input" type="text" class="form-control input-sm form_chat_message" name="message" placeholder="Type your comment here..." /><input id="id_name" value="'+user_key+'" type="hidden" name="key" /><input value="" class="data_id" type="hidden" name="id" /><span class="input-group-btn"><button class="btn btn-success btn-sm" id="btn-chat">Send</button></span></form></div></div></div></div>').appendTo('body');
    if (typeof cookieValue === "undefined") {
        $.ajax({
            url: CHAT_URL+ '?key=' + user_key,
            async:false,dataType: 'JSONP',callback: 'response',
            success: function(response) {
                $('.chat_button_div').show();
                $('.chat_button_div #chat_name_label').attr('data-collapsed', response.button);
                $('.chat_button_div .button_submit').addClass(response.user_id);
            }
        });
    }
    else{
        $('.chat_div_popup').show();
        $('.checkbox_button').trigger('click');
        $.ajax({
            url: COOKIE_URL+ '?cookie=' + cookieValue,
            async:false,dataType: 'JSONP',callback: 'response',
            success: function(data) {
                var response_data = data[0].response;
                var chat_data = data[1].chatapi;
                $('.chat_button_div #chat_name_label').attr('data-collapsed', chat_data.button);
                $('.chat_button_div .button_submit').addClass(chat_data.user_id);
                $('.chat_div_popup .panel-heading').text('Request Notified to '+chat_data.user_name);
                $('.chat_div_popup .data_id').val(chat_data.id);
                var channel = pusher.subscribe(String(chat_data.api_key));
                channel.bind('visitor_message', append_message)
                for (i=0 ; i<response_data.length; i++) {
                    append_message(response_data[i]);
                }
            }
        })
    }
    
    $(document).on('submit', '.chat_form_submit', function(e){
        var form_data = $(".chat_form_submit").serialize();
        e.preventDefault();
        $.ajax({
            url: REQUEST_URL+ '?' + form_data,
            async:false,dataType: 'JSONP',callback: 'response',
            success: function(data) {
                $('.chat_button_div').hide();
                $('.chat_div_popup').show();
                $('.chat_div_popup .panel-heading').text('Request Notified to '+data.user_name);
                $('.chat_div_popup .data_id').val(data.id);
                var cookieValue = $.cookie('api_key', data.api_key);
                var channel = pusher.subscribe(String(data.api_key));
                channel.bind('visitor_message', append_message)
            }
        });
    });
    //Katja Kassin,  moushmi chatterjee
    function append_message(data){
        if (data.user_type == "type") {
            if (data.chat == "start") {
                $('.visitor_type').text(data.message+' is typing');
            }else{
                $('.visitor_type').text(data.message+' has stopped typing');
            }
            $('.visitor_type').show();
        }else{
            if (data.chat == "visitor") {
                var add_div = $('<li class="left clearfix"><span class="chat-img pull-left"><img src="'+STATIC_URL+'uploads/'+data.image+'" alt="User Avatar" class="img-circle added_image" /></span><div class="chat-body clearfix"><div class="header"><strong class="primary-font "> '+data.name+' </strong><small class="pull-right text-muted label label-danger"><i class="icon-time"></i>'+data.time+'</small></div><br /><p>'+data.message+'</p></div></li>');
            }else{
                var add_div = $('<li class="right clearfix"><span class="chat-img pull-right"><img src="'+STATIC_URL+'img/demoUpload.jpg" alt="User Avatar" class="img-circle added_image" /></span><div class="chat-body clearfix"><div class="header"><small class=" text-muted label label-info"><i class="icon-time"></i>'+data.time+'</small><strong class="pull-right primary-font"> '+data.name+' </strong></div><br /><p>'+data.message+'</p></div></li>');
            }
            add_div.appendTo('.chat_append_message');
        }
    }
    
    $(document).on('submit', '.visitor_form_chat', function(e){
        var form_data = $(".visitor_form_chat").serialize();
        e.preventDefault();
        $.ajax({
            url: MESSAGE_URL+ '?' + form_data,
            async:false,dataType: 'JSONP',callback: 'response',
            success: function(data) {
                $('.form_chat_message').val('');
                append_message(data);
            }
        });
    });
    
    $(document).on('click', '.close_button', function(e){
            if (confirm("Are you sure to close the chat") == true) {
                data_id = $('.data_id').val();
                $.ajax({
                url: CLOSE_URL+ '?chat_id='+data_id,
                async:false,dataType: 'JSONP',callback: 'response',
                success: function(data) {
                        $('.chat_append_message li').remove();
                        $('.chat_div_popup').hide();
                        $('.chat_button_div').show();
                        $.removeCookie('api_key');
                    }
                });
            }
    });
    $(document).on('keydown', '.form_chat_message', function(){
        var data = $(this).data();
        if(!data['pressed'])
        {
            data['pressed'] = true;
            var key = $('.data_id').val();
            $.ajax({
                url: TYPE_URL+ '?chat=visitor&type=start&chat_id='+key,
                async:false,dataType: 'JSONP',callback: 'response'
            });
        }
    });
    
    var delay = (function(){
                var timer = 0;
                return function(callback, ms){
                    clearTimeout (timer);
                    timer = setTimeout(callback, ms);
                };
            })();
    
    $(document).on('keyup', '.form_chat_message', function(){
        var data = $(this).data();
        delay(function(){
        data['pressed'] = false;
        var key = $('.data_id').val();
        $.ajax({
            url: TYPE_URL+ '?chat=visitor&type=stop&chat_id='+key,
            async:false,dataType: 'JSONP',callback: 'response'
        });
        }, 1000 );
    });
    
});