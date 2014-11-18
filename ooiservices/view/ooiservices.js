var BASE_URL = 'http://localhost:5000/';
function getForm(url_val) {
    $.ajax({
         type: "GET",
         url: url_val,
         contentType: "application/json; charset=utf-8",
         dataType: "json",
         success: function (data, status, jqXHR) {
               return document.write(JSON.stringify(data));
         },
         error: function (jqXHR, status) {
             return document.write(jqXHR.responseText);
         }
    });
}
function getArrays () {
    var url_val = BASE_URL + "array";
    getForm(url_val);
}
function getPlatform (platform_id) {
    var url_val = BASE_URL + "platform/" + platform_id;
    getForm(url_val);
}
function getInstrument (instrument_id) {
    var url_val = BASE_URL + "instrument/" + instrument_id;
    getForm(url_val);
}
function getPlatformsAtArray (array_id) {
    var url_val = BASE_URL + "platform?array_id=" + array_id;
    getForm(url_val);
}
function getInstrumentsAtPlatform (platform_id) {
   var url_val = BASE_URL + "instrument?platform_id=" + platform_id;
    getForm(url_val);
}
