$(document).ready(function(){
    // all regex patterns to be used
    var RE_EMAIL = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    var RE_NAME = /^[a-zA-Z][a-zA-Z\s]{1,40}$/;
    var RE_PHONE = /^\d{9,12}$/;
    var RE_NUMBER = /^[0-9]*$/;
    var RE_ALPHANUMERIC = /^[a-zA-Z0-9]+$/;

    var companyForm = function() {
        form = document.forms['company-form']; // form data

        // if(form['p_contact'].value) {
        //     if (!RE_PHONE.test(form['p_contact'].value)) {
        //         $('#p_contact-error').text('Enter a proper no.');
        //         return false;
        //     } else {
        //         $('#p_contact-error').text('');
        //     }
        // }

        if(form['s_contact'].value) {
            if (!RE_PHONE.test(form['s_contact'].value)) {
                $('#s_contact-error').text('Enter a proper no.');
                return false;
            } else {
                $('#s_contact-error').text('');
            }
        }

       if(!form['p_email'].value) {
            $('#p_email-error').text('Field Required');
            return false;
        } else if (!RE_EMAIL.test(form['p_email'].value)) {
            $('#p_email-error').text('Enter a proper Email Id.');
            return false;
        } else {
            $('#p_email-error').text('');
        }

        if (form['s_email'].value) {
            if (!RE_EMAIL.test(form['s_email'].value)) {
                $('#s_email').text('Enter a proper Email Id.');
                return false;
            } else {
                $('#s_email').text('');
            }
        }

        if (form['t_email'].value) {
            if (!RE_EMAIL.test(form['t_email'].value)) {
                $('#t_email').text('Enter a proper Email Id.');
                return false;
            } else {
                $('#t_email').text('');
            }
        }

    }

     $('#company-form-id').submit(companyForm);

    var staffForm = function() {
        form = document.forms['staff-form']; // form data
        // primary phone
        if (!form['username'].value) {
                $('#p_number-error').text('Field Required');
            return false;
        } else if (!RE_PHONE.test(form['username'].value)) {
            $('#p_number-error').text('Enter a proper no.');
            return false;
        } else {
            $('#p_number-error').text('');
        }

        // primary email
        if (form['email'].value) {
            if (!RE_EMAIL.test(form['email'].value)) {
                $('#p_email').text('Enter a proper Email Id.');
                return false;
            } else {
                $('#p_email').text('');
            }
        }

        if (form['s_mobile'].value) {
        // secondary phone
            if (!RE_PHONE.test(form['s_mobile'].value)) {
                $('#s_mobile-error').text('Enter a proper no.');
                return false;
            } else {
                $('#s_mobile-error').text('');
            }
        }

}

    // $('#staff-form-id').change(staffForm);
    $('#staff-form-id').submit(staffForm);

    var customerForm = function() {
        form = document.forms['customer-form']; // form data

        if(form['p_mobile'].value) {
            if (!RE_PHONE.test(form['p_mobile'].value)) {
                $('#p-mobile-error').text('Enter a proper no.');
                return false;
            } else {
                $('#p-mobile-error').text('');
            }
        }

        if(form['s_mobile'].value) {
            if (!RE_PHONE.test(form['s_mobile'].value)) {
                $('#s_mobile-error').text('Enter a proper no.');
                return false;
            } else {
                $('#s_mobile-error').text('');
            }
        }


        if(form['t_mobile'].value) {
            if (!RE_PHONE.test(form['t_mobile'].value)) {
                $('#t_mobile-error').text('Enter a proper no.');
                return false;
            } else {
                $('#t_mobile-error').text('');
            }
        }

        if(!form['p_email'].value) {
            $('#p_email-error').text('');
        } else if (!RE_EMAIL.test(form['p_email'].value)) {
            $('#p_email-error').text('Enter a proper Email Id.');
            return false;
        } else{
            $('#p_email-error').text('');
        }

        if(form['s_email'].value) {
            if (!RE_EMAIL.test(form['s_email'].value)) {
                $('#s_email-error').text('Enter a proper Email Id.');
                return false;
            } else {
                $('#s_email-error').text('');
            }
        }

        if(form['t_email'].value) {
            if (!RE_EMAIL.test(form['t_email'].value)) {
                $('#t_email-error').text('Enter a proper Email Id.');
                return false;
            } else {
                $('#t_email-error').text('');
            }
        }

        if(form['q_email'].value) {
            if (!RE_EMAIL.test(form['q_email'].value)) {
                $('#q_email-error').text('Enter a proper Email Id.');
                return false;
            } else {
                $('#q_email-error').text('');
            }
        }
    }

    // $('#customer-form-id').change(customerForm);
    $('#customer-form-id').submit(customerForm);


    var enquiryForm = function() {
        form = document.forms['enquiry-form']; // form data
        if (!form['customer'].value) {
                $('#customer-error').text('Field Required');
            return false;
        }

        if(form['contact'].value) {
            if (!RE_PHONE.test(form['contact'].value)) {
                $('#contact-error').text('Enter a proper no.');
                return false;
            } else {
                $('#contact-error').text('');
            }
        }

    }

    // $('#enquiry-form-id').change(enquiryForm);
    $('#enquiry-form-id').submit(enquiryForm);

    var orderForm = function() {
        form = document.forms['order-form']; // form data
        if (!form['customer'].value) {
                $('#customer-error').text('Field Required');
            return false;
        } else {
            $('#customer-error').text('');
        }

        // var chks = $('input[name=emails]:checkbox');
        // // var chks= document.getElementsByTagName('emails');
        //     var hasChecked = false;
        //     for (var i = 0; i < chks.length; i++)
        //     {
        //         if (chks[i].checked)
        //         {
        //         hasChecked = true;
        //         break;
        //         }
        //     }

        //     if (hasChecked == false)
        //         {
        //         $('#form-emails-error').text('Email Required');
        //         return false;
        //         }

        //     return true;

    }

    // $('#order-form-id').change(orderForm);
    $('#order-form-id').submit(orderForm);

    var complainForm = function() {
        form = document.forms['complain-form']; // form data
        if (!form['customer'].value) {
                $('#customer-error').text('Field Required');
            return false;
        } else {
            $('#customer-error').text('');
        }
    }

    $('#complian-form-id').submit(complainForm);

    var feedbackForm = function() {
        form = document.forms['feedback-form']; // form data
        if (!form['customer'].value) {
                $('#customer-error').text('Field Required');
            return false;
        } else {
            $('#customer-error').text('');
        }
    }

    $('#feedback-form-id').submit(feedbackForm);

});
// end of document ready
