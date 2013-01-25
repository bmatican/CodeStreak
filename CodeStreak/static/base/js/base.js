$(document).ready(function(){
  $('#facebook-button').button();

  $('#facebook-button').click(function() {
    $(this).button('loading');
  });
});

facebookAppId = '377224379022058';
facebookDefaultScope = ["email", "user_about_me", "user_birthday", "user_website"];
staticUrl = '/static/'; 
function facebookJSLoaded(){ 
  FB.init({appId: facebookAppId, status: true, cookie: true, xfbml: true, oauth: true});
} 
window.fbAsyncInit = facebookJSLoaded;
F = new facebookClass(facebookAppId);
F.load();
