var host = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '')+'/';

// Django Ajax CSRF Token Support
    $(document).ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        try{
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }catch(e){$app.debug(e);}
        }
    });


    scripts = document.getElementsByTagName("script");
    var staticPath = scripts[scripts.length-1].src;
    function cleanUp(url) {
        var url = $.trim(url);
        if(url.search(/^https?\:\/\//) != -1)
            url = url.match(/^https?\:\/\/([^\/?#]+)(?:[\/?#]|$)/i, "");
        else
            url = url.match(/^([^\/?#]+)(?:[\/?#]|$)/i, "");
        return url[0];
    }
    staticPath = cleanUp(staticPath);


    // ajax call for Qutation details
    function quotationDetails(quotationId) {
        $(".buy4industry-loader").fadeIn();
        $.ajax({
            type : "GET",
            url : host+"enquiry/api/v1/quotation/"+quotationId+"/detail.json",
            success: function(success) {
                console.log("success"+JSON.stringify(success));
                $(".buy4industry-loader").fadeOut();
                $('#enquiry-data').html(success[0].enquiry);
                $('#quattion-view-order-link').html('<a href="/enquiry/quotation/'+success[0].id+'/detail/">View orders</a>')
                var quotationDate = new Date(success[0].date);
                var newDate = getDateFormate(quotationDate)
                // var newTime = getTimeFormate(quotationDate);
                timeStamp = newDate
                $('#date-data').html(timeStamp);
                var productData = '';
                var i=0;
                if(success[1].products.length) {
                    $("#product-data").removeClass("padding-10px");
                    for (product in success[1].products){
                        i = i+1;
                        productData = productData + '<div class="col-lg-12 no-padding complete-gray-border white-back center"><div class="col-lg-1 gray-left-right-border center padding-5px">'+i+'</div><div class="col-lg-4 gray-left-right-border row-padding center no-padding table-over-flow-coloum textOverflowPopup">'+success[1].products[product].name+'</div><div class="col-lg-3 gray-left-right-border row-padding center no-padding">'+success[1].products[product].quantity+'</div><div class="col-lg-2 gray-left-right-border row-padding center no-padding table-over-flow-coloum textOverflowPopup">'+success[1].products[product].prices_each+'</div><div class="col-lg-2 gray-left-right-border row-padding center no-padding">'+success[1].products[product].net_price+'</div></div>';
                    }
                }else {
                    productData = 'No Data!';
                    $("#product-data").addClass("padding-10px");
                }

                $("#product-data").html(productData);

                $('#delivery-data').html(success[0].delivery);
                $('#freight-data').html(success[0].freight);
                $('#other-data').html(success[0].others);
                $('#payment-data').html(success[0].payment_terms);
                $('#taxes-data').html(success[0].taxes);


            },
            error: function(error) {
                $(".buy4industry-loader").fadeOut();
            }
        });
    }


    // ajax call for Qutation details
    function orderDetails(orderId) {
        $(".buy4industry-loader").fadeIn();
        $.ajax({
            type : "GET",
            url : host+"enquiry/api/v1/order/"+orderId+"/detail.json",
            success: function(success) {
                console.log("success"+JSON.stringify(success));
                $(".buy4industry-loader").fadeOut();
                $('#po_number-data').html(success.po_number || 'NA');
                var deliveryDate = new Date(success.delivery_date);
                var newDate = getDateFormate(deliveryDate)
                var newTime = getTimeFormate(deliveryDate);
                timeStamp = newDate
                $('#date-data').html(timeStamp || 'NA');
                $('#material-data').html(success.material || 'NA');
                $('#special-data').html(success.is_special || 'NA');
                $('#status-data').html(success.get_status_display || 'NA');
            },
            error: function(error) {
                $(".buy4industry-loader").fadeOut();
            }
        });
    }

    //GET TIME IN FROMATE HH:MM AM/PM
    function getTimeFormate(date) {
        var hours = date.getHours();
        var minutes = date.getMinutes();
        var ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        minutes = minutes < 10 ? '0'+minutes : minutes;
        var strTime = hours + ':' + minutes + ' ' + ampm;
        return strTime;
    }
    //END OF GET TIME

    //GET DATE FROMATE IN MMM DD, YYYY EX: Jun 13, 1994
    function getDateFormate(date) {
        var month =["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec"];
        var MMM = month[date.getMonth()];
        var DD = date.getDate();
        var YYYY = date.getFullYear();
        var settime = MMM+" "+DD+", "+YYYY;
        return settime;
    }
    //END OF DATE FROMATE


    $("#customer-list select").change(function(){
        var value = $(this).val();
        console.log("value"+value);
        getEmails(value);
    });
    function getEmails(value) {
        $(".buy4industry-loader").fadeIn();
        $.ajax({
            type:'GET',
            url: host+"customer/api/v1/emails/"+value+".json",
            success : function(success) {
                $(".buy4industry-loader").fadeOut();
                console.log("data"+JSON.stringify(success));
                var emails = '';
                if(success.length) {
                    for (email in success) {
                        emails = emails + '<input type="checkbox" name="emails" value='+success[email]+'>'+success[email]+'<br>';
                    }
                    $("#company-emails").html(emails);
                    $(".email-hide").show();
                } else {
                    $("#company-emails").html('');
                    $(".email-hide").hide();
                }

            },
            error : function (error) {
                $(".buy4industry-loader").fadeOut();
                $("#company-emails").html("");
                $(".email-hide").hide();
            }

        });
    }


    // search api
    function customerSerachApi() {
        $("#id_customer").val('');
        inputVal = $("#search-input > input").val() || '';
        $.ajax({
            type : 'GET',
            url : host+"customer/api/v1/customers/"+inputVal+".json",
            success : function(success) {
                console.log("success "+JSON.stringify(success));
                searchList = '';
                if(success.length) {
                    for(company in success) {
                        searchList = searchList + "<li id="+success[company].id+" class='cursor-pointer search-list-val'>"+success[company].company_name+"</li>";
                    }
                    $("#search-result ul").html(searchList);
                    $("#search-result").show("blind",200);
                } else {
                    $("#search-result ul").html(searchList);
                    $("#search-result").hide("blind",200);
                }

            },
            error : function(error) {
                console.log("error "+JSON.stringify(error));
                $("#search-result").hide("blind",200);
            }
        });
    };



