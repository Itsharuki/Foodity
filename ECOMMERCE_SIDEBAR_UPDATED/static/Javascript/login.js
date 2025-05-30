//#############################################################################
//#####################  F O R G O T  P A S S  P O P U P  #####################
//#############################################################################

function toggle(){
    var blur = document.getElementById('blur');
    blur.classList.toggle('active');
    var popup_forgot_pass = document.getElementById('popup_forgot_pass');
    popup_forgot_pass.classList.toggle('active');
}
