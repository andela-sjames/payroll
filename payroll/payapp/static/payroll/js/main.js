$.ajaxSetup({
    headers: {
        "X-CSRFToken": $("meta[name='csrf-token']").attr("content"),
        'Cache-Control': 'no-store'
    },
});
$.ajaxSetup({ cache: false });

function buildPayRollTable(dataObj, report_id) {

    if ($('#payroll_card').hide()) {
        $('#payroll_card').show();
    }

    var obj = JSON.parse(dataObj);
    $('#payroll').DataTable({
        data: obj,
        dom: 'Bfrtip',
        "bDestroy": true,
        columns: [
            { data: 'employee_id' },
            { data: 'pay_period' },
            { data: 'amount' }
        ],
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ]
    })
}

function buildPayTable(dataObj, report_id) {

    if ($('#pay_card').hide()) {
        $('#pay_card').show();
    }
    var obj = JSON.parse(dataObj);
    $('#pay').DataTable({
        data: obj,
        dom: 'Bfrtip',
        "bDestroy": true,
        columns: [
            { data: 'date' },
            { data: 'hours' },
            { data: 'employee_id' },
            { data: 'job_group' }
        ],
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ]
    })
}

function getPayroll(report_id) {
    $.ajax({
        type: "GET",
        url: `/pay/payroll/${report_id}`,
        
        success: function(data) {
            if (data.status == "success") {
                // check if we are on the home page or 
                // report page
                if (window.location.pathname == '/') {
                    var button  = $('#uploadcsv').find('button');
                    button.attr("disabled", false);
                } 
                buildPayRollTable(data.data, report_id)
            } else {
                M.toast({html: data.msg, classes: 'rounded', displayLength: 3000});
            }
        }
    })
}

function getReport(report_id) {
    $.ajax({
        type: "GET",
        url: `/pay/report/${report_id}`,
        
        success: function(data) {
            if (data.status == "success") {
                buildPayTable(data.data, report_id)
            } else {
                M.toast({html: data.msg, classes: 'rounded', displayLength: 3000});
            }
        }
    })
}

function fetchReport() {
    $('#fetch_report').on('submit', function(event) {
        event.preventDefault();
        var $form = $(this);

        var fd = new FormData();
        var other_data = $form.serializeArray();

        $.each(other_data, function(key, input) {
            fd[input.name] = input.value;
        });

        if (fd.report_type === "payroll") {
            getPayroll(fd.report)
        } else {
            getReport(fd.report)
        }
    })
}

function uploadForm() {
    $('#uploadcsv').on('submit', function(event) {
        event.preventDefault();
        var $form = $(this);

        var button  = $('#uploadcsv').find('button');
        button.attr('disabled', 'disabled');
        $form.find('p').remove();

        // display Uploading...
        M.toast({html: 'Uploading...', 
            classes: 'rounded', 
            displayLength: 300,
            inDuration: 600
        });

        var fd = new FormData();
        var file_data = $form.find('input[type="file"]')[0].files[0];
        fd.append("csv_file", file_data);

        var other_data = $form.serializeArray();
        $.each(other_data, function(key, input) {
            fd.append(input.name, input.value);
        });

        $.ajax({
            type: "POST",
            url: '/pay/upload/',
            data: fd,
            contentType:false,
            processData: false,

            success: function(data) {
                if (data.status == "success") {
                    // display Getting Report...(preloader)
                    var report_id = data.report_id

                    // set report in case page is refreshed. 
                    localStorage.setItem('payapp_payroll', report_id);
                    getPayroll(report_id)

                } else {
                    button.attr("disabled", false);
                    M.toast({html: data.msg, classes: 'rounded', displayLength: 3000});
                }
            },

            error: function(error) {
                console.log(error.responseText)
                M.toast({html: "An Error Occurred While Uploading File.", classes: 'rounded', displayLength: 3000});
            },

            headers: {
                "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val()
            },
        })
    })
}

function refreshPayroll () {
    // only run if we are on the homepage
    if (window.location.pathname == '/') {
        var report_id = localStorage.getItem('payapp_payroll');
        if (report_id !== null) {
            getPayroll(report_id)
        } else {
            // hide the payroll_card
            $('#payroll_card').hide();
        }
    }
}

function reportPage() {
    // only run when we are on report page. 
    if (window.location.pathname === '/pay/report/') {
        $('#pay_card').hide();
        $('#payroll_card').hide();
    }
}

function initProps() {
    // for dropdown, tooltips and select option.
    $('select').formSelect();
    $(".dropdown-content li>span").css("color", "#42A5F5");
    $('.tooltipped').tooltip();
}

$(document).ready(function(){
    uploadForm();
    refreshPayroll();
    initProps();
    reportPage();
    fetchReport();
})
