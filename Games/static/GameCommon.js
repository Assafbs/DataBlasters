// consts:
var c_numQuestionsPerGame = 5;
var c_pointsPerQuestion = 10;

// global vars:
var correctAnswer = false;


function onCorrectAnswer(elemId) {
  document.getElementById(elemId).style.background='#00e600';
  disableAllAnswersButtons();
  correctAnswer = true;
  changePointsText(c_pointsPerQuestion);
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
    var questionNum =  parseInt(getCookiebyName('questionNum'));
    if (questionNum == c_numQuestionsPerGame){
      document.getElementById('next').innerHTML = "Finish Game";
    }
    document.getElementById("pointsForAns").style.visibility = "visible";
    document.getElementById("next").style.visibility = "visible";
}

function changePointsText(points) {
    document.getElementById('pointsForAns').innerHTML = "You won " + points + " points for that answer!";
}

function Redirect(path) {
  var points = 0;
  if (correctAnswer){
    points = c_pointsPerQuestion;
    correctAnswer = false;
  }
  document.cookie = 'points='.concat(points.toString());
  document.cookie = 'allowAccess=true'
  window.location.href = path;
}

var getCookiebyName = function(name){
	var pair = document.cookie.match(new RegExp(name + '=([^;]+)'));
	return !!pair ? pair[1] : null;
};