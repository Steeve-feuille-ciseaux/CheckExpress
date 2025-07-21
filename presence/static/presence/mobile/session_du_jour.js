function toggleParticipant(element) {
    const checkbox = element.querySelector('input[type="checkbox"]');
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        element.classList.toggle('selected');
        updateCounter();
    }
}

function selectAll() {
    document.querySelectorAll('.participants-grid input[type="checkbox"]').forEach(cb => {
        cb.checked = true;
        cb.closest('.participant-item').classList.add('selected');
    });
    updateCounter();
}

function clearAll() {
    document.querySelectorAll('.participants-grid input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        cb.closest('.participant-item').classList.remove('selected');
    });
    updateCounter();
}

function updateCounter() {
    const selectedItems = document.querySelectorAll('.participant-item.selected');
    document.getElementById('selectedCount').textContent = selectedItems.length;
}

updateCounter();