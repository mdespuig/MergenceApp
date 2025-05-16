document.addEventListener('DOMContentLoaded', function timelineSelectionInit() {
    function getTimelineCsrfToken() {
        let csrfToken = null;
        document.cookie.split(";").forEach(cookie => {
            const trimmedCookie = cookie.trim();
            if (trimmedCookie.startsWith("csrftoken=")) {
                csrfToken = decodeURIComponent(trimmedCookie.substring("csrftoken=".length));
            }
        });
        return csrfToken;
    }

    function updateTimelineSelectionCount() {
        const totalBoxes = document.querySelectorAll('.rowCheckbox').length;
        const selectedBoxes = document.querySelectorAll('.rowCheckbox:checked').length;
        const selectionText = document.getElementById('selectionCount');
        if (selectionText) {
            selectionText.textContent = `${selectedBoxes} of ${totalBoxes} selected`;
        }
    }

    function clearTimelineSelection() {
        document.querySelectorAll('.rowCheckbox').forEach(box => box.checked = false);
        const selectAllBox = document.getElementById('selectAll');
        if (selectAllBox) selectAllBox.checked = false;
        updateTimelineSelectionCount();
    }

    window.clearSelection = clearTimelineSelection;

    document.querySelectorAll('.rowCheckbox').forEach(box => {
        box.addEventListener('change', updateTimelineSelectionCount);
    });

    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const isChecked = this.checked;
            document.querySelectorAll('.rowCheckbox').forEach(box => box.checked = isChecked);
            updateTimelineSelectionCount();
        });
    }

    const timelineDeleteBtn = document.querySelector('.timelineDeleteBtn');
    if (timelineDeleteBtn) {
        timelineDeleteBtn.addEventListener('click', function () {
            const checkedBoxes = Array.from(document.querySelectorAll('.rowCheckbox:checked'));
            const idsToDelete = checkedBoxes.map(box => box.getAttribute('data-id'));

            if (idsToDelete.length === 0) {
                alert("No entries selected.");
                return;
            }

            if (!confirm(`Delete ${idsToDelete.length} selected entr${idsToDelete.length > 1 ? 'ies' : 'y'}?`)) return;

            fetch('/bulk-delete-timeline-entries/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getTimelineCsrfToken(),
                },
                body: JSON.stringify({ ids: idsToDelete }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    checkedBoxes.forEach(box => {
                        const row = box.closest('tr');
                        if (row) row.remove();
                    });
                    updateTimelineSelectionCount();
                } else {
                    alert("Failed to delete entries.");
                }
            })
            .catch(() => alert("An error occurred while deleting entries."));
        });
    }
});

