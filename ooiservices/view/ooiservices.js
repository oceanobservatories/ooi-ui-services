var BASE_URL = 'http://localhost:4000/';
function getForm(url_val, callback) {
    jQuery.ajax({
         type: "GET",
         url: url_val,
         contentType: "application/json; charset=utf-8",
         dataType: "json",
         success: function (data) {
            result = JSON.stringify(data, null, 2)
            callback(result);
         },
         error: function (jqXHR, status) {
            return document.write(jqXHR.responseText);
         }
    });
}
function getArrays () {
    var url_val = BASE_URL + "arrays";
    getForm(url_val, function(result) {
        $("#out").html(result);
    });

}
function getPlatform (platform_id) {
    var url_val = BASE_URL + "platforms/" + platform_id;
    getForm(url_val, function(result) {
        $("#out").html(result);
    });
}
function getInstrument (instrument_id) {
    var url_val = BASE_URL + "instruments/" + instrument_id;
    getForm(url_val, function(result) {
        $("#out").html(result);
    });
}
function getStream (stream_id) {
    var url_var = BASE_URL + "streams/" + stream_id;
    getForm(url_val, function(result) {
        $("#out").html(result);
    });
}
function getPlatformsAtArray (array_id) {
    var url_val = BASE_URL + "platforms?array_id=" + array_id;
    getForm(url_val, function(result) {
        $("#out").html(result);
    });
}
function getInstrumentsAtPlatform (platform_id) {
   var url_val = BASE_URL + "instruments?platform_id=" + platform_id;
   getForm(url_val, function(result) {
        $("#out").html(result);
    });
}
function getStreamAtInstrument (instrument_id) {
    var url_val = BASE_URL + "streams?instrument_id" + platform_id;
    getForm(url_val, function(result){
        $("#out").html(result);
    });
}