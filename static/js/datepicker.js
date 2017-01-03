$(document).ready(function() {
    // add profile date picker
    $('#datetimepicker-last_called').datetimepicker({
        // pick12HourFormat: true,
        format: "YYYY-MM-DD hh:mm A",
        icons : {

                    date: 'fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                    previous: 'fa fa fa-chevron-left',
                    next: 'fa fa-chevron-right',
                    today: 'fa fa-crosshairs',
                    clear: 'fa fa-trash',
                    close: 'fa fa-times',
                    time: 'fa fa-clock-o',
                },
    });

    $('#delivery-date, #order-delivery-date, #gr-date, #billing-date').datetimepicker({
        format: "YYYY-MM-DD",
        icons : {
                    time: 'fa fa-clock-o',
                    date: 'fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                    previous: 'fa fa fa-chevron-left',
                    next: 'fa fa-chevron-right',
                    today: 'fa fa-crosshairs',
                    clear: 'fa fa-trash',
                    close: 'fa fa-times',
                },
    });


});
