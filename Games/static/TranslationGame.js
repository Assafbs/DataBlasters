// consts:
var c_numQuestionsPerGame = 5;
var c_pointsPerQuestion = 10;

// global vars:
var questionNum = 0;
var correctAnswer = false;


function onCorrectAnswer(elemId) {
  document.getElementById(elemId).style.background='#00e600';
  disableAllAnswersButtons();
  questionNum++;
  correctAnswer = true;
  changePointsText(c_pointsPerQuestion);
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
    var qNum =  parseInt(getCookiebyName('questionNum'));
    if (qNum == c_numQuestionsPerGame){
      document.getElementById('next').innerHTML = "Finish Game";
    }
    document.getElementById("pointsForAns").style.visibility = "visible";
    document.getElementById("next").style.visibility = "visible";
}

function changePointsText(points) {
    document.getElementById('pointsForAns').innerHTML = "You won " + points + " points for that answer";
}

function Redirect() {
  var points = 0;
  if (correctAnswer){
    points = c_pointsPerQuestion;
    correctAnswer = false;
  }
  document.cookie = 'points='.concat(points.toString());
  window.location.href = '../translateGame_';
}

var getCookiebyName = function(name){
	var pair = document.cookie.match(new RegExp(name + '=([^;]+)'));
	return !!pair ? pair[1] : null;
};