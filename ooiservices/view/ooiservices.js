function getPlatform (array_code) {
    if (array_code) {
        var url_val = "http://localhost:5000/" + array_code + "/platforms";
    } else {
        var url_val = "http://localhost:5000/platforms";
    }
    jQuery.ajax({
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

function getInstrument (platform_id) {
    if (platform_id) {
        var url_val = "http://localhost:5000/" + platform_id + "/instrument";
    } else {
        var url_val = "http://localhost:5000/instrument";
    }
    jQuery.ajax({
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