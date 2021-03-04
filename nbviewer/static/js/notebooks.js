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


var selectedOutputs = [];

function onCompare(){
    if(selectedOutputs.length == 2){
        var url = "/outputs/?action=compare&output_ids=" + selectedOutputs.join(',');
        var win = window.open(url, '_blank');
        win.focus();
    }
}

function showRunDetailModal(e) {
    var code = $(e).attr('data-code');
    $('#runDetailModal').modal()

    $('#run_logs_table').DataTable({
        processing: true,
        ajax: '/notebooks/?code=' + code + '&action=run_logs&limit=100',
        columns: [
            {
                data: 'id',
                render: function ( data, type, row, meta ) {
                  return `<input data-id="${data}" class="output-row" type="checkbox" />`;
                },
                "orderable": false
            },
            {
                data: 'id'
            },
            {
                data: "exe_date"
            },
            {
                data: "exe_time"
            },
            {
                data: 'code',
                render: function(data, type, row, meta){
                    var url = `/outputs?code=${data}&action=show`
                    return `<a target='_blank' href="${url}">Open</a>`;
                }
            }
        ]
    });

        $('#run_logs_table').on('click', '.output-row', function (e) {
            var id = $(this).attr('data-id');

            var index = selectedOutputs.indexOf(id)
            if(index !== -1){
                selectedOutputs.splice( index, 1 );
                 $("#output_compare").hide()
                return;
            }

            if(selectedOutputs.length == 2){
                e.preventDefault();
                return;
            }

            selectedOutputs.push( id );

            console.log(selectedOutputs);

            if(selectedOutputs.length == 2){
                 $("#output_compare").show()
            }else{
                $("#output_compare").hide()
            }
//            var index = $.inArray(id, selectedOutputs);
//
//            if(selectedOutputs.length == 2){
//                selectedOutputs.pop();
//            }
//            if ( index === -1 ) {
//                selectedOutputs.push( id );
//            } else {
//                selectedOutputs.splice( index, 1 );
//            }

//            $(this).toggleClass('selected');
        } );
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

function changeCronState(target) {
    if (target.checked)
        $('#cron-inputs').slideDown();
    else
        $('#cron-inputs').slideUp();
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

    setTimeout(function () {
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