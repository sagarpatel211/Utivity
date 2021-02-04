//Gets the element from hoursLabel to be turned into id="hours" so timer.html uses it
const hoursLabel = document.getElementById("hours");
//Gets the element from minutesLabel to be turned into id="minutes" so timer.html uses it
const minutesLabel = document.getElementById("minutes");
//Gets the element from secondsLabel to be turned into id="seconds" so timer.html uses it
const secondsLabel = document.getElementById("seconds");
//Gets the element from historyTable to be turned into id="history" so timer.html uses it
const historyTable = document.getElementById("history");
document.getElementById('submit').style.display='none'; //hides the submit button when loading timer.html
document.getElementById('start').style.display = 'inline'; //shows the start button when loading in file

let totalSeconds = 0; //sets variable to count for elapsed time
let interval = undefined; //defines interval to be used to determine how to refresh the time every second

//function start that runs onclick when the start button is pressed
function start() {
    if (!interval) { //if the interval is still undefined
        interval = setInterval(setTime, 1000); //set the interval to 1000ms refresh rate which counts up by seconds
        document.getElementById('submit').style.display = 'inline'; //show the submit button after pressing start
        document.getElementById('start').style.display='none'; //hide the start button once stopwatch begins
    }
}

//function start that runs onclick when the submit button is pressed
function submit() {
    clearInterval(interval); //clear the interval value 
    addRow(); //add a row into the preview table
    interval = undefined; //set the interval back to defined
    totalSeconds = 0; //reset the number of seconds elapsed
    secondsLabel.innerHTML = "00"; //reset the seconds display
    minutesLabel.innerHTML = "00"; //reset the minutes display
    hoursLabel.innerHTML = "00"; //reset the hours display
    document.getElementById('submit').style.display='none'; //hides the submit button after pressed
    document.getElementById('start').style.display = 'inline'; //shows the start button after submit is pressed
}

//Function that adds the submitted data into the preview table to be temporarily stored before being pushed to the db
function addRow() {
    if (!interval) return;
    //If the interval is reset to nothing, then fill in all the two cells with the elapsed time and the start time
    const rowCount = historyTable.rows.length;
    const row = historyTable.insertRow(rowCount);
    const cell1 = row.insertCell(0);
    const cell2 = row.insertCell(1);
    //Formats the time into hours:minutes:seconds and pushes it into the first cell
    cell1.innerHTML = hoursLabel.innerHTML + ":" + minutesLabel.innerHTML + ":" + secondsLabel.innerHTML;
    var time = cell1.innerHTML;
    //Takes the time value and assigns it with an id of time to be used in timer.html
    document.getElementById("time").value = time;
    const date = new Date();
    cell2.innerHTML =
        padding(date.getMonth() + 1) +
        "/" +
        padding(date.getDay()) +
        "/" +
        date.getFullYear();
    var todaydate = cell2.innerHTML;
    //Takes the date value and assigns it with an id of todayday to be used in timer.html
    document.getElementById("todaydate").value = todaydate;
    //sets the interval value back to undefined
    interval = undefined;
}

//Clears the temporary table where the data is stored before being pushed
function clearRows() {
    const rowCount = historyTable.rows.length;
    if (!rowCount) return;
    for (let i = 1; i < rowCount; i++) { //for loop over all items in the row
        historyTable.deleteRow(1); //Main function which deletes all the rows (not columns because those are constants)
    }
}

//setTime function which calculates 
function setTime() {
    ++totalSeconds; //increment the total elapsed time
    const hours = Math.floor(totalSeconds / 3600); //do some math to find the # of hours
    const minutes = Math.floor((totalSeconds - 3600 * hours) / 60); //finds the number of minutes
    const seconds = totalSeconds % 60; //and finds the number of seconds
    secondsLabel.innerHTML = padding(seconds); //created label for seconds
    minutesLabel.innerHTML = padding(minutes); //created label for minutes
    hoursLabel.innerHTML = padding(hours);     //created label for hours
}

//function to control when a number goes from 9 to 10 and above which helps with conversion
//If it is 9 or less, it will concatenate a "0" and "the number", else, just prints the time
function padding(val) {
    return val < 10 ? "0" + val : val;
}

//Functions that are ran when the corresponding button is clicked
(function () {
    document.getElementById("start").onclick = function () {
        start(); //start function is run when start button is pressed
    };
    document.getElementById("submit").onclick = function () {
        submit(); //submit function is run when submit button is pressed
    };})();