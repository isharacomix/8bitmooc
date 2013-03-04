var instanse = false;
var state;
var mes;

function Chat () {
    this.update = updateChat;
    this.send = sendChat;
    this.getState = getStateOfChat;
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


// This returns the current number of strings on the server.
function getStateOfChat() {
	if(!instanse){
		instanse = true;
		$.ajax({
			type: "POST",
			url: "/chat/",
			data: {'function': 'getState', 'channel': channel},
			dataType: "json",	
			success: function(data) {state = data.state;instanse = false;}
		});
	}	
}

// This draws those values
function updateChat() {
	if(!instanse){
		instanse = true;
		$.ajax({
			type: "POST",
			url: "/chat/",
			data: {'function': 'update','state': state,'channel': channel},
			dataType: "json",
			success: function(data) {
				if(data.text){
				    $('#chat-area').html("");
					for (var i = 0; i < data.text.length; i++) {
						$('#chat-area').append(data.text[i] +"<br />");
					}	
				}
				document.getElementById('chat-area').scrollTop = document.getElementById('chat-area').scrollHeight;
				instanse = false;
				state = data.state;
			}
		});
	}
	else {
		setTimeout(updateChat, 1500);
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

