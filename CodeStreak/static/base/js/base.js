function endsWith(str, suffix) {
  return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

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
var contestId;
var lastLogEntry;
var facebookAppId;
var staticUrl;

function setGlobal(name, notInt) {
  if (notInt !== true) {
    notInt = false;
  }
  var ending = "Id", id = name;
  if (!endsWith(id, ending)) {
    id += ending;
  }
  $('#' + id).each(function () {
    var val = $(this).attr('value');
    if (notInt === false) {
      window[name] = parseInt(val, 10);
    } else {
      window[name] = val;
    }
  });
}

function initGlobals() {
  setGlobal("contestId");
  setGlobal("lastLogEntry");
  setGlobal("facebookAppId");
  setGlobal("staticUrl", true);
}

function followPostLink(action) {
  $('<form></form>')
    .attr('method', 'post')
    .attr('action', action)
    .append($('<input type="hidden" name="csrfmiddlewaretoken" />')
      .attr('value', csrfToken))
    .submit();
}

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

function showModal(modalHeader, modalBody, callback) {
  var body, header;
  body = $('#modal-dialog-body');
  body.empty();
  body.append(modalBody);
  header = $('#modal-dialog-header');
  header.empty();
  header.append(modalHeader);
  $('#modal-dialog').modal({
    keyboard: true
  });
  $('#modal-dialog-ok-button').off('click');
  $('#modal-dialog-ok-button').click(function () {
    callback();
    $('#modal-dialog').modal('hide');
  });
  $('#modal-dialog').modal('show');
}

$(document).ready(function () {
  initGlobals();

  $('#facebook-button').button();
  $('#facebook-button').click(function () {
    $(this).button('loading');
  });

  $('.alert').alert();
  $('.collapse').collapse();

  $('.js-post-link').click(function (e) {
    followPostLink($(this).attr('href'));
    return false;
  });
  $('.js-post-btn').click(function (e) {
    followPostLink($(this).attr('data-action'));
    return false;
  });
  $('.js-get-btn').click(function (e) {
    window.location = $(this).attr('data-href');
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

  var oldContestState,
    checkContestState = function () {
      if (!contestId) {
        return;
      }
      var data = {
        'contest_id': contestId
      };
      pullData('getContestState', data, 'get', function (response) {
        if (response.verdict === 'ok') {
          if (oldContestState === undefined) {
            oldContestState = response.message;
          } else if (oldContestState !== response.message) {
            if (response.message === 1) {  // STARTED
              var modalHeader, modalBody;
              modalHeader = $('<p></p>');
              modalHeader.html('Contest has started!');
              modalBody = $('<p></p>');
              modalBody.html('Do you want to be redirected to problem set?');
              showModal(modalHeader, modalBody, function () {
                window.location = '/contest/' + contestId;
              });
            } else if (response.message === 2 || response.message === 3) {
              // PAUSED or STOPPED
              // refresh immediately
              window.location = '/contest/' + contestId;
            }
            oldContestState = response.message;
          }
        } else {
          console.log('Catastrophic failure! Failed to get contest state!');
        }
      });
    };

  setInterval(checkContestState, 2000);

  $('#log-entries').each(function () {
    var fetchLogEntries = function () {
      var data = {
        'contest_id': contestId,
        'last_log_entry': lastLogEntry
      };
      pullData('fetchContestLogs', data, 'get', function (response) {
        if (response.verdict === 'ok') {
          lastLogEntry = response.message.last_log_entry;
          $('#log-entries').prepend(response.message.entries);
          var badges = response.message.badges;
          $('.log-toggle-link').each(function (index, element) {
            var log_id = parseInt($(this).attr('data-log-id'), 10),
              badge = badges[log_id];
            if (badge !== undefined) {
              $(this).empty();
              $(this).append(badge);
            }
          });
          if (response.message.entries !== "") {
            console.log("onContentLoaded");
            onContentLoaded();
          }
        }
      });
    };

    fetchLogEntries();
    setInterval(fetchLogEntries, 2000);
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
  $('#alerts').append($('<div class="alert alert-info">')
    .append('<button data-dismiss="alert" type="button" class="close">x</button>')
    .append(message));
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

// should be called each time new content is loaded and the page is loaded
function activateContent() {
  var showResponse = function (response, element, button) {
    var message, message_style, doReload;
    if (response.verdict === 'success') {
      message = "Answer accepted. Well done! Loading next exercise...";
      message_style = "text-success";
      doReload = true;
    } else if (response.verdict === 'wrong-answer') {
      message = "Wrong Answer";
      message_style = "text-error";
      doReload = true;
    } else if (response.verdict === 'skipped') {
      message = "Task skipped. Loading next exercise...";
      message_style = "text-warning";
      doReload = true;
    } else if (response.verdict === 'error') {
      message = "Server error...";
      message_style = "text-error";
      doReload = false;
    }

    button.button('reset');
    element.html($('<p></p>')
      .attr('class', message_style)
      .append(message));
    element.hide();
    element.fadeIn('normal', function () {
      setTimeout(function () {
        element.fadeOut('normal', null);
      }, 3000);
    });
    if (doReload) {
      setTimeout(function () {
        document.location.reload(true);
      }, 1000);
    }
  };
  $('.submit-form').off('submit');

  $('.submit-form').submit(function (e) {
    var task_id = parseInt($(this).attr('data-task-id'), 10),
      answer = $(this).find('.answer').val(),
      response = $(this).siblings('.task-response'),
      button = $(this).find('.submit-button'),
      data = {
        'task_id': task_id,
        'answer': answer,
        'contest_id': contestId
      };

    response.empty();
    if (answer === '') {
      showAlert("Answer must not be empty");
      return false;
    }
    button.button('loading');
    pullData('submitTask', data, 'post', function (feedback) {
      showResponse(feedback, response, button);
    });

    return false;
  });

  $('.skip-button button').off('click');
  $('.skip-button button').click(function (e) {
    var response = $(this).parent().siblings('.task-response'),
      data = {
        'task_id': parseInt($(this).parent().attr('data-task-id'), 10),
        'contest_id': contestId
      };

    $(this).button('loading');
    pullData('skipTask', data, 'post', function (feedback) {
      showResponse(feedback, response, $(this));
    });
    return false;
  });

  $('.log-toggle-link').off('click');
  $('.log-toggle-link').click(function (e) {
    var logId = parseInt($(this).attr('data-log-id'), 10),
      data = {
        'log_id': logId
      },
      that = $(this);
    pullData('toggleLog', data, 'post', function (feedback) {
      if (feedback.verdict === 'ok') {
        that.empty();
        that.append(feedback.badge);
      } else {
        console.log('error: ', feedback.message);
      }
    });
    return false;
  });

}

function onContentLoaded() {
  activateContent();
}

$(document).ready(function () {
  activateContent();
});

$.fn.animateHighlight = function (duration) {
  var animateMs = duration || 400,
    that = this;
  that.stop().fadeOut(animateMs / 2, function () {
    that.fadeIn(animateMs / 2);
  });
};
