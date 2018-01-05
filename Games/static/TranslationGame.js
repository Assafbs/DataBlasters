
function onCorrectAnswer(elemId) {
  document.getElementById(elemId).style.background='#00e600';
  disableAllAnswersButtons();
  changePointsText(5);
  showNextButtonAndWonPoints();
}


function onWrongAnswer(elemId) {
  document.getElementById(elemId).style.background='#FF0000';
  disableAllAnswersButtons();
  showNextButtonAndWonPoints();
}

function disableAllAnswersButtons() {
  for (i = 1; i <= 4; i++){
    buttonId = "button".concat(i);
    document.getElementById(buttonId).setAttribute('disabled','disabled');
  }
}

function showNextButtonAndWonPoints() {
    document.getElementById("pointsForAns").style.visibility = "visible";
    document.getElementById("next").style.visibility = "visible";
}

function changePointsText(points) {
    document.getElementById('pointsForAns').innerHTML = "You won " + points + " points for that answer";
}

 function Redirect() {
  window.location.href = '../';
}