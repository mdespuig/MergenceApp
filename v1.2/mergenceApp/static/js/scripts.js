function getCSRFToken() {
        const name = 'csrftoken';
        const cookieValue = document.cookie.split('; ')
            .find(row => row.startsWith(name + '='))
            ?.split('=')[1];
        return cookieValue || '';
}

document.addEventListener('DOMContentLoaded', function () {
    const mainHotlineSelect = document.getElementById('main-hotline');
    const subHotlineDivs = document.querySelectorAll('.hotline-sub');

    mainHotlineSelect.addEventListener('change', function () {
        subHotlineDivs.forEach(div => {
            div.style.display = 'none';
        });

        const selected = this.value;
        const target = document.getElementById(selected);
        if (target) {
            target.style.display = 'block';
        }
    });
});

function closePopup() {
    document.getElementById("popup").style.display = "none";
}
window.onload = function () {
    document.getElementById("popup").style.display = "flex";
};

document.addEventListener('DOMContentLoaded', () => {
    const rows = document.querySelectorAll('tbody tr');
    const searchInput = document.getElementById('searchInput');
    const checkboxes = document.querySelectorAll('.rowCheckbox');
    const selectAll = document.getElementById('selectAll');
    const selectionCount = document.getElementById('selectionCount');

    function updateSelectionCount() {
        const visibleCheckboxes = Array.from(checkboxes).filter(
            cb => cb.closest('tr').style.display !== 'none'
        );
        const selected = visibleCheckboxes.filter(cb => cb.checked).length;
        const total = visibleCheckboxes.length;
        selectionCount.textContent = `${selected} of ${total} selected`;
    }

    searchInput.addEventListener('input', () => {
        const value = searchInput.value.toLowerCase();
        rows.forEach(row => {
            const orgName = row.children[2].textContent.toLowerCase();
            row.style.display = orgName.includes(value) ? '' : 'none';
        });
        updateSelectionCount();
    });

    checkboxes.forEach(cb => cb.addEventListener('change', updateSelectionCount));

    if (selectAll) {
        selectAll.addEventListener('change', () => {
            rows.forEach(row => {
                if (row.style.display !== 'none') {
                    const checkbox = row.querySelector('.rowCheckbox');
                    if (checkbox) {
                        checkbox.checked = selectAll.checked;
                    }
                }
            });
            updateSelectionCount();
        });
    }

    window.clearSelection = function () {
        checkboxes.forEach(cb => cb.checked = false);
        if (selectAll) selectAll.checked = false;
        updateSelectionCount();
    };

function updateStatus(newStatus) {
    const selectedIds = [];
    const checkboxes = document.querySelectorAll('.rowCheckbox');

    checkboxes.forEach(cb => {
        if (cb.checked) {
            selectedIds.push(cb.dataset.id);
        }
    });

    if (selectedIds.length === 0) {
        alert("No rows selected.");
        return;
    }

    fetch('/update_partner_status/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            ids: selectedIds,
            status: newStatus
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to update status.");
        return response.json();
    })
    .then(data => {
        if (data.success) {
            checkboxes.forEach(cb => {
                if (cb.checked) {
                    const row = cb.closest('tr');
                    const statusCell = row.querySelector('td:last-child .status');
                    if (statusCell) {
                        statusCell.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                        statusCell.className = `status ${newStatus}`;
                        row.dataset.status = newStatus;
                        cb.checked = false;
                    }
                }
            });
            const selectAll = document.getElementById('selectAll');
            if (selectAll) selectAll.checked = false;
            updateSelectionCount();
        } else {
            alert("Failed to update status. Please try again.");
        }
    })
    .catch(error => {
        console.error("Error updating status:", error);
        alert("An error occurred while updating the status.");
    });
}

document.querySelector('.approve').addEventListener('click', () => updateStatus('Approved'));
document.querySelector('.reject').addEventListener('click', () => updateStatus('Rejected'));
});

document.addEventListener('DOMContentLoaded', () => {
  const selectAll = document.getElementById('selectAll');
  const checkboxes = document.querySelectorAll('.rowCheckbox');
  const selectionCount = document.getElementById('selectionCount');
  
  function updateSelectionCount() {
    const visibleCheckboxes = Array.from(checkboxes).filter(cb => cb.closest('tr').style.display !== 'none');
    const selected = visibleCheckboxes.filter(cb => cb.checked).length;
    const total = visibleCheckboxes.length;
    selectionCount.textContent = `${selected} of ${total} selected`;
  }

  checkboxes.forEach(cb => cb.addEventListener('change', updateSelectionCount));

  if (selectAll) {
    selectAll.addEventListener('change', () => {
      const checked = selectAll.checked;
      checkboxes.forEach(cb => {
        if (cb.closest('tr').style.display !== 'none') {
          cb.checked = checked;
        }
      });
      updateSelectionCount();
    });
  }

  window.clearSelection = function () {
    checkboxes.forEach(cb => cb.checked = false);
    if (selectAll) selectAll.checked = false;
    updateSelectionCount();
  };

  const deleteButton = document.querySelector('.delete');
  if (deleteButton) {
    deleteButton.addEventListener('click', () => {
      const selectedIds = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.dataset.id);

      if (selectedIds.length === 0) {
        alert("No users selected to delete.");
        return;
      }

      if (!confirm(`Are you sure you want to delete ${selectedIds.length} user(s)? This action cannot be undone.`)) {
        return;
      }

      fetch('/delete_users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ ids: selectedIds })
      })
      .then(response => {
        if (!response.ok) throw new Error('Failed to delete users');
        return response.json();
      })
      .then(data => {
        if (data.success) {
          selectedIds.forEach(id => {
            const cb = document.querySelector(`.rowCheckbox[data-id="${id}"]`);
            if (cb) {
              const row = cb.closest('tr');
              row.remove();
            }
          });
          updateSelectionCount();
          alert('Users deleted successfully.');
        } else {
          alert('Failed to delete users.');
        }
      })
      .catch(error => {
        console.error('Delete error:', error);
        alert('An error occurred while deleting users.');
      });
    });
  }
const saveButton = document.querySelector('.save');
if (saveButton) {
  saveButton.addEventListener('click', () => {
    const updates = [];

    document.querySelectorAll('.userTypeDropdown').forEach(select => {
      updates.push({
        id: select.dataset.id,
        user_type: select.value
      });
    });

    fetch('/save_user_roles/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({ updates: updates })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('User types updated successfully.');
      } else {
        alert('Failed to update user types.');
        console.error(data.error);
      }
    })
    .catch(error => {
      console.error('Error updating user types:', error);
      alert('An error occurred while updating user types.');
    });
  });
}
});

document.addEventListener("DOMContentLoaded", function () {
    if (window.ticketId) {
        showToast(`✅ Ticket ${window.ticketId} found!`);
        const section = document.getElementById("ticket-section");
        if (section) {
            section.style.display = "block";
        }
    }
});

function showToast(message) {
    const toast = document.getElementById("toast-popup");
    const toastMsg = document.getElementById("toast-message");

    toastMsg.textContent = message;
    toast.style.display = "block";
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => {
            toast.style.display = "none";
        }, 300);
    }, 3000);
}

document.getElementById('assign-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    const response = await fetch("{% url 'assign_responder' %}", {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        },
        body: formData
    });

    const result = await response.json();
    showToast(result.message, result.status === 'success');
});

function showToast(message, success = true) {
    const toast = document.createElement('div');
    toast.className = 'custom-toast';
    toast.textContent = message;
    toast.style.backgroundColor = success ? '#28a745' : '#dc3545';

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 3000);
}

function handleEditButton(button) {
  const row = button.closest('tr');
  const entryId = button.getAttribute('data-id');
  const titleCell = row.querySelector('.title-cell');
  const currentTitle = titleCell.textContent.trim();

  titleCell.innerHTML = `
    <input type="text" class="edit-input" value="${currentTitle.replace(/"/g, '&quot;')}" />
    <button class="btn btn-save">Save</button>
    <button class="btn btn-cancel">Cancel</button>
  `;

  button.style.display = 'none';

  const input = titleCell.querySelector('.edit-input');
  const saveBtn = titleCell.querySelector('.btn-save');
  const cancelBtn = titleCell.querySelector('.btn-cancel');

  input.focus();

  saveBtn.addEventListener('click', () => {
    const newTitle = input.value.trim();
    if (newTitle === '') {
      alert('Title cannot be empty.');
      input.focus();
      return;
    }
    updateEntryTitle(entryId, newTitle, titleCell, button);
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      saveBtn.click();
    }
    if (e.key === 'Escape') {
      cancelBtn.click();
    }
  });

  cancelBtn.addEventListener('click', () => {
    titleCell.textContent = currentTitle;
    button.style.display = 'inline-block';
  });
}

function updateEntryTitle(entryId, newTitle, titleCell, editButton) {
  fetch(`/edit-timeline-entry/${entryId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ title: newTitle }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      titleCell.textContent = newTitle;
      editButton.style.display = 'inline-block';
    } else {
      alert('Update failed.');
      titleCell.textContent = titleCell.querySelector('.edit-input').value;
      editButton.style.display = 'inline-block';
    }
  })
  .catch(() => {
    alert('Update failed.');
    titleCell.textContent = titleCell.querySelector('.edit-input').value;
    editButton.style.display = 'inline-block';
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}



