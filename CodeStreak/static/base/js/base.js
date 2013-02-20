function getCookie(name) {
  var cookieValue = null, cookies, cookie, i;
  if (document.cookie && document.cookie !== '') {
    cookies = document.cookie.split(';');
    for (i = 0; i < cookies.length; i += 1) {
      cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
var csrfToken = getCookie('csrftoken');

$(document).ready(function () {
  $('#facebook-button').button();
  $('#facebook-button').click(function () {
    $(this).button('loading');
  });

  $('.alert').alert();
  $('.collapse').collapse();

  $('.post-link').click(function (e) {
    $('<form></form>')
      .attr('method', 'post')
      .attr('action', $(this).attr('href'))
      .append($('<input type="hidden" name="csrfmiddlewaretoken" />')
        .attr('value', csrfToken))
      .submit();
    return false;
  });

  $('#time-left').each(function () {
    var
      timeLeft = parseInt($(this).attr('class'), 10),
      that = this,
      intervalID = -1,

      formatTimeRemaining = function (rem) {
        var s, m, h;
        s = rem % 60;
        rem = Math.floor(rem / 60);
        m = rem % 60;
        rem = Math.floor(rem / 60);
        h = rem;
        return (("00" + h).slice(-2) + ':' +
                ("00" + m).slice(-2) + ':' +
                ("00" + s).slice(-2));
      },
      updateTimeLeft = function () {
        $(that).html('Time left: ' + formatTimeRemaining(timeLeft));
        timeLeft -= 1;
        if (timeLeft < 0) {
          clearInterval(intervalID);
          $(that).parent().remove();
        }
      };
    updateTimeLeft();
    intervalID = setInterval(updateTimeLeft, 1000);
  });
});

var facebookDefaultScope = ["email", "user_about_me", "user_birthday", "user_website"];
function facebookJSLoaded() {
  FB.init({appId: facebookAppId, status: true, cookie: true, xfbml: true, oauth: true});
}
window.fbAsyncInit = facebookJSLoaded;
var F = new facebookClass(facebookAppId);
F.load();

function showAlert(message) {
  $('#alerts').append('<div class="alert alert-info"><button data-dismiss="alert" type="button" class="close">x</button>' + message + '</div>');
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
  // test that a given url is a same-origin URL
  // url could be relative or scheme relative or absolute
  var host = document.location.host, // host + port
    protocol = document.location.protocol,
    sr_origin = '//' + host,
    origin = protocol + sr_origin;
  // Allow absolute or scheme relative URLs to same origin
  return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
    (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') ||
    // or any other URL that isn't scheme relative or absolute i.e relative.
    !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
      // Send the token to same-origin, relative URLs only.
      // Send the token only if the method warrants CSRF protection
      // Using the CSRFToken value acquired earlier
      xhr.setRequestHeader("X-CSRFToken", csrfToken);
    }
  }
});

function pullData(provider, payload, type, callback) {
  var request = $.ajax({
    url: "/data_provider/" + provider,
    type: type,
    data: {
      "payload": JSON.stringify(payload)
    }
  });

  request.done(function (response, textStatus, jqXHR) {
    callback(JSON.parse(response));
  });
}


function taskCallback(feedback, task_no) {
  setTimeout(function () {
    var button = $('#answerbutton' + task_no),
      response = $('#taskresponse' + task_no),
      response_message,
      message,
      message_style,
      doReload;

    button.button('reset');
    if (feedback.verdict === 'success') {
      message = "Answer accepted. Well done! Loading next exercise...";
      message_style = "text-success";
      doReload = true;
    } else if (feedback.verdict === 'wrong-answer') {
      message = "Wrong Answer";
      message_style = "text-error";
      doReload = true;
    } else if (feedback.verdict === 'skipped') {
      message = "Task skipped. Loading next exercise...";
      message_style = "text-warning";
      doReload = true;
    } else if (feedback.verdict === 'error') {
      message = "Server error...";
      message_style = "text-error";
      doReload = false;
    }

    response.append('<p id="responsemessage' + task_no +
                    '" class="' + message_style + '" style="display:none">' +
                    message + '</p>');
    response_message = $('#responsemessage' + task_no);
    response_message.fadeIn('slow', function () {
      setTimeout(function () {
        response_message.fadeOut('slow', null);
        if (doReload) {
          document.location.reload(true);
        }
      }, 3000);
    });
  }, 500);
}

function submitTask(task_no) {
  var answer = $('#taskanswer' + task_no).val(),
    response = $('#taskresponse' + task_no),
    button = $('#answerbutton' + task_no),
    data = {
      'task_id': task_no,
      'answer': answer,
      'contest_id': contestId
    };

  response.empty();
  if (answer === '') {
    showAlert("Answer must not be empty");
    return;
  }
  button.button('loading');
  pullData('submitTask', data, 'post', function (feedback) {
    taskCallback(feedback, task_no);
  });
}

function skipTask(task_id) {
  var data = {
    'task_id' : task_id,
    'contest_id' : contestId
  };
  pullData('skipTask', data, 'post', function (feedback) {
    taskCallback(feedback, task_id);
  });
}
