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
    
    // create and write to a file called metadata.txt, then download in Chrome
    download(jsonData, "metadata.txt", "text/plain")
}