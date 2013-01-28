$(document).ready(function(){
  $('#facebook-button').button();

  $('#facebook-button').click(function() {
    $(this).button('loading');
  });
});
$(".alert").alert();
$(".collapse").collapse()

facebookDefaultScope = ["email", "user_about_me", "user_birthday", "user_website"];
function facebookJSLoaded(){
  FB.init({appId: facebookAppId, status: true, cookie: true, xfbml: true, oauth: true});
}
window.fbAsyncInit = facebookJSLoaded;
F = new facebookClass(facebookAppId);
F.load();

function showAlert(message) {
  $('#alerts').append('<div class="alert alert-info"><button data-dismiss="alert" type="button" class="close">x</button>' + message + '</div>');
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length +1));
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
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin +
'/') ||
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

function pullData(action_x, payload_x, callback ) {
  var request = $.ajax({
    url: "/pula",
    type: "post",
    data: {
            action: action_x,
            payload: JSON.stringify(payload_x)
         }
  });

  request.done(function (response, textStatus, jqXHR){
    callback(JSON.parse(response));
  });

}

function submitTask(task_no) {
  var answer = $('#taskanswer'+task_no).val();
  response = $('#taskresponse'+task_no);
  response.empty();
  button=$('#answerbutton'+task_no);
  if (answer == '') {
    showAlert("Answer must not be empty");
    return;
  }
  button.button('loading');
  var data = {
               'task_no' : task_no,
               'answer' : '' + answer
             }
  pullData('submitTask', data, function(feedback) {
    setTimeout(function() {
      button.button('reset');
      if (feedback.verdict == 'success') {
        var message = "Answer accepted. Well done! Loading next exercise.";
        var message_style = "text-success";
        var doReload = true;
      }
      response.append('&nbsp;<p id="responsemessage' + task_no + 
                      '" class="'+message_style+'" style="display:none">' + 
                      message + '</p>');
      response_message = $('#responsemessage' + task_no);
      response_message.fadeIn('slow', function() {
        setTimeout(function() {
          response_message.fadeOut('slow', null);
          if (doReload) document.location.reload(true);
        }, 3000);
      });
    }, 500);
  });
}
