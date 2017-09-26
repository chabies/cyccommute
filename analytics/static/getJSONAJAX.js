//This function makes a request using a url and receives a response from the corresponding view
jQuery.extend({
                getValues: function(url) {
                    var result = null;
                    $.ajax({
                        url: url,
                        type: 'get',
                        dataType: 'json',
                        async: false,
                        success: function(data, textStatus, jqXHR) {
                            result = data;
                            }
                        });
                    return result;
                }
            });