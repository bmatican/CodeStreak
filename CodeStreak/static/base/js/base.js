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
