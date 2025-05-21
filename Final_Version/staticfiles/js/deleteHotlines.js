document.addEventListener('DOMContentLoaded', function hotlineSelectionInit() {
    function getHotlineCsrfToken() {
        let token = null;
        document.cookie.split(';').forEach(cookie => {
            const c = cookie.trim();
            if (c.startsWith('csrftoken=')) {
                token = decodeURIComponent(c.substring('csrftoken='.length));
            }
        });
        return token;
    }

    function updateHotlineSelectionCount() {
        const totalCheckboxes = document.querySelectorAll('.rowCheckbox').length;
        const selectedCheckboxes = document.querySelectorAll('.rowCheckbox:checked').length;
        const countElem = document.getElementById('selectionCount');
        if (countElem) {
            countElem.textContent = `${selectedCheckboxes} of ${totalCheckboxes} selected`;
        }
    }

    function clearHotlineSelection() {
        document.querySelectorAll('.rowCheckbox').forEach(cb => cb.checked = false);
        const selectAllBox = document.getElementById('selectAll');
        if (selectAllBox) selectAllBox.checked = false;
        updateHotlineSelectionCount();
    }

    window.clearSelection = clearHotlineSelection;

    document.querySelectorAll('.rowCheckbox').forEach(cb => {
        cb.addEventListener('change', updateHotlineSelectionCount);
    });

    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const isChecked = this.checked;
            document.querySelectorAll('.rowCheckbox').forEach(cb => cb.checked = isChecked);
            updateHotlineSelectionCount();
        });
    }

    const hotlineDeleteBtn = document.querySelector('.hotlineDelete');
    if (hotlineDeleteBtn) {
        hotlineDeleteBtn.addEventListener('click', function () {
            const selectedBoxes = Array.from(document.querySelectorAll('.rowCheckbox:checked'));
            const idsToDelete = selectedBoxes.map(cb => cb.getAttribute('data-id'));

            if (idsToDelete.length === 0) {
                alert('No hotlines selected.');
                return;
            }

            if (!confirm(`Delete ${idsToDelete.length} selected hotlin${idsToDelete.length > 1 ? 'es' : 'e'}?`)) return;

            fetch('/bulk-delete-hotlines/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getHotlineCsrfToken(),
                },
                body: JSON.stringify({ ids: idsToDelete }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    selectedBoxes.forEach(cb => {
                        const row = cb.closest('tr');
                        if (row) row.remove();
                    });
                    updateHotlineSelectionCount();
                } else {
                    alert('Failed to delete hotlines.');
                }
            })
            .catch(() => alert('An error occurred while deleting hotlines.'));
        });
    }
});
