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

var host = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '')+'/';

$(document).ready(function(){

    console.log('Jquery ok');

    // hide success message
    setTimeout(function() {
        $('.success-message, .error-message, .successbox ').slideUp(500);
    },5000);
    // end hide success messge function

    $(document).ready(function(){
      var element = $('.table-over-flow-coloum');
      $.each(element, function(index, val) {
         if( (element[index].offsetHeight < element[index].scrollHeight) || (element[index].offsetWidth < element[index].scrollWidth)){
          $(element[index]).addClass('textOverflowPopup');
        }
      });
    });

    $(document).on('click', '.textOverflowPopup', function(){
      $('#textOverflowPopup #textOverflowPopup-container').html($(this).html());
      $('#textOverflowPopup').modal('show');
    });

});

$(document).ready(function(){
      var element = $('.title-over-flow-coloum');
      $.each(element, function(index, val) {
         if( (element[index].offsetHeight < element[index].scrollHeight) || (element[index].offsetWidth < element[index].scrollWidth)){
          $(element[index]).addClass('titleOverflowPopup');
        }
      });
});

$(window).load(function() {
    $(".buy4industry-loader").fadeOut();
});

// JS for sub menu slide of Frame
$('#user-menu').click(function(){
    $('#user-sub-menu').slideToggle(function(){
      if(typeof(Storage) !== "undefined") {
        if($('#user-sub-menu').is(':hidden')){
          sessionStorage.noticeStatus = 0;
        }else{
          sessionStorage.noticeStatus = 1;
        }
      }
    });
});

$('#user-menu').ready(function(){
      if(typeof(Storage) !== "undefined") {
        if (sessionStorage.noticeStatus == 1) {
            $('#user-sub-menu').show();
        }
      }
});


$('.gray-form-border > input').click(function(event){
    event.stopPropagation();
    $('.form-input-shadow').removeClass('form-input-shadow');
    $(this).addClass('form-input-shadow');

});

// JS for delete confirmation
$('#ask-to-delete').click(function(){
    if ($('.list-checkbox input:checked').length > 0) {
        $('#delete-confirm-modal').modal('show');
    }
});

// JS to handle all select checkbox
$('#checked-all > input').click(function(event) {
    if(this.checked) {
      // Iterate each checkbox
        $('.list-checkbox input:checkbox').each(function() {
            this.checked = true;
        });
}
    else {
        $('.list-checkbox input:checkbox').each(function() {
              this.checked = false;
        });
    }
});

$("#password-eye").click(function(){
    $("#id_password").attr("type", 'text');
});

$(".clear-radio").click(function(){
    $('input[name=status]').prop('checked',false);
    $('input[name=through]').prop('checked',false);
    $('input[name=company]').prop('checked',false);
    $('input[name=is_special]').prop('checked',false);
    $('input[name=customer_code]').prop('checked',false);
    $('input[name=company_type]').prop('checked',false);
});

// JS to handle image prv
function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
               $('#customer-profile-img-prv > img').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

$("#id_image").change(function(){
    readURL(this);
});

$('#customer-file-img, #customer-profile-img-prv > img').click(function(){
    $('#id_image').click();
});

// $('#stock-file, #order-file').click(function(){
//     $('#id_file').click();
//     $('#id_file_upload').click();
// });

// function for active menu background
$(function(){
    var url = window.location.href;
    $("#menu-list a").each(function() {
        if(url == (this.href)) {
            $(this).children("li").addClass("active-menu");
        }
    });
});

$("#quotation-details-id-0").addClass("blue-active");

$("#quotation-outer-box > div").click(function() {
    $("#quotation-outer-box > div").removeClass("blue-active");
    $(this).addClass("blue-active");
});

$("#quotation-details-id-0").addClass("blue-active");

$("#quotation-outer-box > div").click(function() {
    $("#quotation-outer-box > div").removeClass("blue-active");
    $(this).addClass("blue-active");
});

$(".permission-input-master input").change(function() {
    if(this.checked) {
        $( ".permission-input input" ).prop( "checked", "checked" );
        $( ".permission-input input" ).prop("disabled", "disabled");
    }
    else {
        $( ".permission-input input" ).removeAttr( "checked");
        $( ".permission-input input" ).removeAttr("disabled");
    }
});

$(document).click(function(){
    $("#search-result").hide("blind",200);
});

var textVal;
$('.search-list-val').css('cursor','pointer');
$(document).on('click touchstart', '.search-list-val', function(event) {
    event.preventDefault();
    textVal = $(this).text();
    id = $(this).prop('id');
    $("#search-input > input").val(textVal);
    $("#search-result").hide("blind",200);
    $("#id_customer").val(id);
});



/*$('.date-filter').click(function(){
    oldVal = $('#enquiry-filter-form #order_by').val();
    if(oldVal == 'date' || oldVal == ''){
        $('#enquiry-filter-form #order_by').val('-date');
    }else{
        $('#enquiry-filter-form #order_by').val('date');
    }
    $("#enquiry-filter-form").submit();
});*/
