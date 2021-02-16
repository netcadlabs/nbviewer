$(document).ready(function () {
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
    $('#nb-form #file').change(function (e) {
        var fileName = e.target.files[0].name;
        fileName = fileName.slice(0, fileName.lastIndexOf('.'));
        if (!$('#name').val() || !$('#name').val().trim()) {
            $('#name').val(fileName)
        }
    });

    $(function () {
        $('[data-toggle="popover"]').popover()
    })
});

function showErrorDetailModal(e) {
    var detail = $(e).attr('data-error');
    $('#error-details').text(detail);
    $('#errorDetailModal').modal()
}

function showRunDetailModal(e) {
    var code = $(e).attr('data-code');
//    var detail = $(e).attr('data-error');
//    $('#run-details').text(detail);
    $('#runDetailModal').modal()
    $('#run_logs_table').empty();
    $.ajax({
            url: '/notebooks/?code=' + code + '&action=run_logs',
            type: 'GET'
        }).done(function (res) {
            console.log("delete success");
            //TODO - use data table?
            if(res && res.data){
                for(var i = 0 ; i < res.data.length; i++){
                    item = res.data[i];
                    html = '<tr>';
                    html += `<td>${item['exe_date']}</td>`;
                     html += `<td>${item['exe_time']}</td>`;
                     if(item['error'])
                        html += `<td>ERROR</td>`;
                     else
                        html += `<td>OK</td>`;

                     $('#run_logs_table').append(html)
                }
            }
        })
        .fail(function () {

        });
}

function deleteNb(code) {
    var question = confirm('Are you sure to delete this notebook?');
    if (question) {
        $.ajax({
            url: '/notebooks/?code=' + code + '&action=delete',
            type: 'GET'
        }).done(function () {
            console.log("delete success");
            $("#nb-" + code).remove();
        })
            .fail(function () {
                console.error("delete failed");
            });
    }
}

function runNb(code) {
    notebookControls(code, true)
    $.ajax({
        url: '/notebooks/?code=' + code + '&action=run',
        type: 'GET'
    }).done(function (result) {
        console.log(result);
    })
        .fail(function (result) {
            console.error(result);
        }).always(function (result) {
            notebookControls(code, false)
            console.log('always ' + JSON.stringify(result))
        });
}

function notebookControls(code, disable) {
    var c = '#nb-' + code + ' .nb-controls-col button'
    $(c).attr('disabled', disable)
}

function updateNotebookStatus(code, runResult) {
    if (!runResult) return;

    if (runResult.result) {

    } else {

    }
}

function changeIntervalType(target) {
    var type = $(target).val()

    $('#interval-every').hide();
    $('#interval-each').hide();
    $('#interval-' + type).show();

    //    console.log($(target).val())
}

function copyTextToClipboard(elem, text) {
    if (!validURL(text))
        text = window.location.origin + text;
    var input = document.createElement('input');
    input.setAttribute('value', text);
    document.body.appendChild(input);
    input.select();
    var result = document.execCommand('copy');
    document.body.removeChild(input);

    setTimeout(function(){
        $(elem).popover('hide');
    }, 1500)
}

function validURL(str) {
    var pattern = new RegExp('^(https?:\\/\\/)?' + // protocol
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
        '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
        '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
        '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
    return !!pattern.test(str);
}