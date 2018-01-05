var questionNum = 0;
var numQuestionsPerGame = 1;


function onCorrectAnswer(elemId) {
  document.getElementById(elemId).style.background='#00e600';
  disableAllAnswersButtons();
  questionNum++;
  changePointsText(5);
  showNextButtonAndWonPoints();
}


function onWrongAnswer(elemId) {
  document.getElementById(elemId).style.background='#FF0000';
  disableAllAnswersButtons();
  questionNum++;
  showNextButtonAndWonPoints();
}

function disableAllAnswersButtons() {
  for (i = 1; i <= 4; i++){
    buttonId = "button".concat(i);
    document.getElementById(buttonId).setAttribute('disabled','disabled');
  }
}

function showNextButtonAndWonPoints() {
    if (questionNum == numQuestionsPerGame){
      document.getElementById('next').innerHTML = "Finish Game";
    }
    document.getElementById("pointsForAns").style.visibility = "visible";
    document.getElementById("next").style.visibility = "visible";
}

function changePointsText(points) {
    document.getElementById('pointsForAns').innerHTML = "You won " + points + " points for that answer";
}

 function Redirect() {
  if (questionNum == numQuestionsPerGame){
    window.location.href = '../'; //TODO: route to game selection page
  }
  else {
    window.location.href = '../'; //TODO: route to other question
  }
}