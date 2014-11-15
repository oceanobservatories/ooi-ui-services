var BASE_URL = 'http://localhost:5000/';
function getPlatform (platform_id) {
    if (platform_id) {
        var url_val = BASE_URL + "platforms/" + platform_id;
    } else {
        var url_val = BASE_URL + "platforms";
    }
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
function getInstrument (instrument_id) {
    if (instrument_id) {
        var url_val = BASE_URL + "instrument/" + instrument_id;
    } else {
        var url_val = BASE_URL + "instrument";
    }
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