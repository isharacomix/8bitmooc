var instanse = false;
var state;
var mes;

function Chat () {
    this.update = updateChat;
    this.send = sendChat;
}


// Get the CSRF token - from the Django docs.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


// This draws those values
function updateChat(force) {
	if(!instanse){
		instanse = true;
		$.ajax({
			type: "POST",
			url: "/chat/",
			data: {'function': 'update','state': state,'channel': channel, 'force':force},
			dataType: "json",
			success: function(data) {
				if(data.messages){
				    $('#chat-area').html("");
					for (var i = 0; i < data.messages.length; i++) {
					    if ( data.messages[i][4] )
						$('#chat-area').append("<div class=\"media\"><a class=\"pull-left\" href=\"/~"+data.messages[i][0]+"\">"+data.messages[i][1]+"</a><div class=\"media-body\"><strong>"+data.messages[i][0]+": </strong> "+data.messages[i][2] +"<a href=\"#\" onclick=\"upvote("+data.messages[i][4]+");return false;\"><i class=\"icon-plus-sign\"></i></a><a href=\"#\" onclick=\"downvote("+data.messages[i][4]+");return false;\"><i class=\"icon-minus-sign\"></i><text class=\"muted\"> ("+data.messages[i][5]+")</text></div></div>");
						else
						$('#chat-area').append("<div class=\"media\"><a class=\"pull-left\" href=\"/~"+data.messages[i][0]+"\">"+data.messages[i][1]+"</a><div class=\"media-body\"><strong>"+data.messages[i][0]+": </strong> "+data.messages[i][2] +"<text class=\"muted\"> ("+data.messages[i][5]+")</text></div></div>");
					}	
				}
				document.getElementById('chat-area').scrollTop = document.getElementById('chat-area').scrollHeight;
				instanse = false;
				state = data.state;
			}
		});
	}
}

//send the message
function sendChat(message, nickname) { 
	updateChat();
	$.ajax({
		type: "POST",
		url: "/chat/",
		data: {'function': 'send','message': message,'nickname': nickname,'channel': channel},
		dataType: "json",
		success: function(data){
			updateChat();
		}
	});
}


// Send an upvote
function upvote(comment_id) {
	$.ajax({
		type: "POST",
		url: "/chat/",
		data: {'function': 'upvote', 'comment': comment_id, 'channel': channel},
		dataType: "json",
		success: function(data){
			updateChat(true);
		}
	});
}

// send a downvote
function downvote(comment_id) {
	$.ajax({
		type: "POST",
		url: "/chat/",
		data: {'function': 'downvote', 'comment': comment_id, 'channel': channel},
		dataType: "json",
		success: function(data){
			updateChat(true);
		}
	});
}


