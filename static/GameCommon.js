// consts:
var c_numQuestionsPerGame = 5;
var c_pointsPerQuestion = 20;

// global vars:
var correctAnswer = false;


function onCorrectAnswer(answerNum) {
    document.getElementById('button'.concat(answerNum.toString())).style.background = '#00e600';
    disableAllAnswersButtons();
    correctAnswer = true;
    changePointsText(c_pointsPerQuestion);
    showNextButtonAndWonPoints();
}


function onWrongAnswerShowRight(answerNum) {
    var correctAnswerNum = parseInt(getCookieByName('correctAnswerNum'));
    document.getElementById('button'.concat(answerNum.toString())).style.background = '#FF0000';
    document.getElementById('button'.concat(correctAnswerNum.toString())).style.background = '#ffcc33';
    disableAllAnswersButtons();
    showNextButtonAndWonPoints();
}

function onAnswer(answerNum) {
    var correctAnswerNum = parseInt(getCookieByName('correctAnswerNum'));
    if (answerNum === correctAnswerNum) {
        onCorrectAnswer(answerNum);
    }
    else {
        onWrongAnswerShowRight(answerNum);
    }
}

function disableAllAnswersButtons() {
    var buttonId;
    for (var i = 1; i <= 4; i++) {
        buttonId = "button" + i;
        document.getElementById(buttonId).setAttribute('disabled', 'disabled');
    }
}

function showNextButtonAndWonPoints() {
    var questionNum = parseInt(getCookieByName('questionNum'));
    if (questionNum === c_numQuestionsPerGame) {
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
    if (correctAnswer) {
        points = c_pointsPerQuestion;
        correctAnswer = false;
    }
    document.cookie = 'points='.concat(points.toString());
    document.cookie = 'allowAccess=true';
    window.location.href = path;
}

var getCookieByName = function (name) {
    var pair = document.cookie.match(new RegExp(name + '=([^;]+)'));
    return !!pair ? pair[1] : null;
};
