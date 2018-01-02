
function onCorrectAnswer(elemId) {
  document.getElementById(elemId).style.background='#00e600';
  alert("correct answer!");
}


function onWrongAnswer(elemId) {
  document.getElementById(elemId).style.background='#FF0000';
  alert("wrong answer!");
}