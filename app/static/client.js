var el = x => document.getElementById(x);
const POSITIVES = ["Sweet! I can smell some Jollof",
                   "Nice! This what we call JOLLOF",
                   "I didn't have to look, This is JOllof!"];

const NEGATIVES = ["Nope! Not Jollof",
                   "Sorry! this can't be jollof",
                   "Not Jollof"];
function showPicker() {
  el("file-input").click();
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

function analyze() {
  var uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

  el("analyze-button").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true);
  xhr.onerror = function() {
    alert(xhr.responseText);
    el("analyze-button").innerHTML = "Analyze";
  };
  xhr.onload = function(e) {
    if (this.readyState === 4) {
      var response = JSON.parse(e.target.responseText);
      el("result-label").innerHTML =  funnyText(response);
    }
    el("analyze-button").innerHTML = "Analyze";
  };
  

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}

function funnyText(response) {
  let text = response["result"] === 'jollof' && response["pro"][0] > 50 ? "It's Jollof" : "Nope! Not Jollof.";
  let probability = Math.floor(response["pro"][0] * 100);
  let confidence = "My Confidence level " + probability + "%";
  return text + "\n" + confidence;
}

