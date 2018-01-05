
function onCorrectAnswer(elemId) {
  document.getElementById(elemId).style.background='#00e600';
  disableAllAnswersButtons();
  showNextButton();

  //setTimeout('Redirect()', 10000); //TODO: test it!
  //window.prompt("sometext","defaultText");
}


function onWrongAnswer(elemId) {
  document.getElementById(elemId).style.background='#FF0000';
  disableAllAnswersButtons();
  showNextButton();
}

function disableAllAnswersButtons() {
  for (i = 1; i <= 4; i++){
    buttonId = "button".concat(i);
    document.getElementById(buttonId).setAttribute('disabled','disabled');
  }
}

function showNextButton() {
    document.getElementById("next").style.visibility = "visible";
}


 function Redirect() {
   window.location="http://www.tutorialspoint.com";
} //TODO: test it (and change the url...)