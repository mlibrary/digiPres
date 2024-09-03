// this is a function that downloads a string to a text file in browser
// to your local Downloads folder
function downloadString(text, filename, mimeType) {
    var blob = new Blob([text], { type: mimeType });
    var url = window.URL.createObjectURL(blob);
  
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
  
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

// this is a function that will collect values from metadata form,
// put them into JSON format, then write and download to metadata.txt file
function convertToJson() {
    let form = document.getElementById("dataForm");
    let formData = {};
    // loop through form data and put name, value pairs into JSON object
    for (let i = 0; i < (form.elements.length - 1); i++) {
        let element = form.elements[i];
        if (element.type !== "submit") {
            formData[element.name] = element.value;
        }
    }

    // convert to string format and add newlines for aesthetic
    let jsonData = JSON.stringify(formData, "", " ");

    // print to console log in browser
    console.log(jsonData)

    // create and write to a file called metadata.txt, then download in browser
    downloadString(jsonData, "metadata.txt", "text/plain")

}
