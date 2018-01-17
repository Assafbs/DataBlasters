function Redirect(path) {
    document.cookie = 'allowAccess=true';
    window.location.href = path;
}

function validateForm() {
    var song1 = document.forms["answers"]["song1"].value;
    var song2 = document.forms["answers"]["song2"].value;
    var song3 = document.forms["answers"]["song3"].value;
    var song4 = document.forms["answers"]["song4"].value;
    if ((song1 === song2) || (song1 === song3) || (song1 === song4) || (song2 === song3) || (song2 === song4) || (song3 === song4)) {
        document.getElementById("sameSong").style.visibility = "visible";
        return false;
    }
    else {
        document.getElementById("sameSong").style.visibility = "hidden";
    }
}