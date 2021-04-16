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
    var code = $(e).attr('data-code');
    selectedNotebookCode = code;
    $('#error-details').text(detail);
    $('#errorDetailModal').modal()
}


var selectedOutputs = [];
var selectedNotebookCode = null;
var outputTable = null;

function onCompare() {
    if (selectedOutputs.length == 2) {
        var url = "/outputs/?action=compare&output_ids=" + selectedOutputs.join(',');
        var win = window.open(url, '_blank');
        win.focus();
    }
}

function onOutputClear(){
    if(!selectedNotebookCode)
        return;
    
    var question = confirm('Are you sure to delete all outputs of this notebook?');

    if (question) {
        $.ajax({
            url: '/outputs/?code=' + selectedNotebookCode + '&action=delete',
            type: 'DELETE'
        }).done(function () {
            console.log("delete notebook outputs success");
            $('#runDetailModal').modal('hide')
            $('#errorDetailModal').modal('hide')
        })
        .fail(function () {
            console.error("delete notebook outputs failed");
        });
    }
}

function showRunDetailModal(e) {
    var code = $(e).attr('data-code');
    selectedNotebookCode = code;

    $('#runDetailModal').modal()
    outputTable = $('#run_logs_table').DataTable({
        processing: true,
        destroy: true,
        ajax: '/notebooks/?code=' + code + '&action=run_logs&limit=100',
        columns: [
            {
                data: 'id',
                render: function (data, type, row, meta) {
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
                data: "exe_time",
                render: function (data, type, row, meta) {
                    var exe_time = Number(data).toFixed(2)
                    return exe_time;
                }
            },
            {
                data: 'code',
                render: function (data, type, row, meta) {
                    var url = `/outputs?code=${data}&action=show`
                    return `<a target='_blank' href="${url}">Open</a>`;
                }
            }
        ]
    });

    outputTable.on( 'draw', function () {
        if(outputTable && outputTable.rows().count()){
            $("#output_clear").show()
        }
    } );

    $("#output_compare").hide()
    selectedOutputs = [];

    $('#run_logs_table').on('click', '.output-row', function (e) {
        var id = $(this).attr('data-id');

        var index = selectedOutputs.indexOf(id)
        if (index !== -1) {
            selectedOutputs.splice(index, 1);
            $("#output_compare").hide()
            return;
        }

        if (selectedOutputs.length == 2) {
            e.preventDefault();
            return;
        }

        selectedOutputs.push(id);
        if (selectedOutputs.length == 2) {
            $("#output_compare").show()
        } else {
            $("#output_compare").hide()
        }
    });
}

function updateNb(code){
    if(!code) return;

    selectedNotebookCode = code;
//    notebookControls(code, true);

    $('#update_notebook_code').val(code)
    $('#updateNotebookModal').modal();
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