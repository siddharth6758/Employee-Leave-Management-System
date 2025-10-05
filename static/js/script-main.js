$(document).ready(function() {

    if ($('#leaveDetailModal').length === 0) {
        const modalHtml = `
            <div id="leaveDetailModal" class="modal">
                <div class="modal-content">
                    <span class="modal-close-button">&times;</span>
                    <h2>Leave Request Details</h2>
                    <div class="modal-body">
                        <p><strong>Employee:</strong> <span id="modal-employee"></span></p>
                        <p><strong>Leave Type:</strong> <span id="modal-type"></span></p>
                        <p><strong>Start Date:</strong> <span id="modal-start"></span></p>
                        <p><strong>End Date:</strong> <span id="modal-end"></span></p>
                        <p><strong>Reason:</strong></p>
                        <blockquote id="modal-reason"></blockquote>
                    </div>
                </div>
            </div>`;
        $('body').append(modalHtml);
    }


    function openModal(data) {
        $('#modal-employee').text(data.employee);
        $('#modal-type').text(data.type);
        $('#modal-start').text(data.start);
        $('#modal-end').text(data.end);
        $('#modal-reason').text(data.reason);
        $('#leaveDetailModal').fadeIn(200);
    }

    function closeModal() {
        $('#leaveDetailModal').fadeOut(200);
    }


    // Use event delegation for click events on `.leave-request-item`
    $('body').on('click', '.leave-request-item', function(event) {
        // Stop if the click was on the approval/reject buttons
        if ($(event.target).closest('.approval-buttons').length) {
            return;
        }

        // Get data from the clicked item's data-* attributes
        const data = {
            employee: $(this).data('employee'),
            type: $(this).data('type'),
            start: $(this).data('start'),
            end: $(this).data('end'),
            reason: $(this).data('reason'),
        };

        openModal(data);
    });

    $('body').on('click', '.modal-close-button', function() {
        closeModal();
    });

    $(window).on('click', function(event) {
        if ($(event.target).is('#leaveDetailModal')) {
            closeModal();
        }
    });

    function getCsrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val();
    }

    function handleLeaveAction(leaveId, actionUrl) {
        $.ajax({
            url: actionUrl,
            type: 'POST',
            data: {
                'leave_id': leaveId,
                'csrfmiddlewaretoken': getCsrfToken()
            },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Error: ' + response.error);
                    $('.leave-request-item').css('opacity', '1');
                }
            },
            error: function(xhr) {
                alert('An error occurred. Please try again.', xhr.responseText);
                console.log(xhr.responseText);
            }
        });
    }

    $('.main-panel').on('click', '.approve-btn', function() {
        if (confirm('Are you sure you want to approve this leave request?')) {
            var leaveId = $(this).data('id');
            handleLeaveAction(leaveId, '/leave-approve/');
        }
    });

    $('.main-panel').on('click', '.reject-btn', function() {
        if (confirm('Are you sure you want to reject this leave request?')) {
            var leaveId = $(this).data('id');
            handleLeaveAction(leaveId, '/leave-reject/');
        }
    });

    $('#report-download-btn').click(function (e) {
    e.preventDefault();

    $.ajax({
      url: '/leave-report-download/',
      method: 'GET',
      xhrFields: {
        responseType: 'blob'  // receive as a Blob
      },
      success: function (data, status, xhr) {
        // extract filename from Content-Disposition header
        var disposition = xhr.getResponseHeader('Content-Disposition');
        var filename = 'download.csv';  // default filename

        if (disposition && disposition.indexOf('filename=') !== -1) {
          filename = disposition.split('filename=')[1].replace(/"/g, '');
        }
        // create Blob and trigger download
        var blob = new Blob([data], { type: 'text/csv' });
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);  // clean up
      },
      error: function (xhr, status, error) {
        alert('Failed to download file: ' + error);
      }
    });
  });

});
