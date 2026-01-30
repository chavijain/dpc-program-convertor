// Data from DPC convertor - Main JavaScript

let sessionId = null;
let currentData = [];
let currentColumns = [];
let selectedRows = new Set();
let isSplitView = false;
let isTransposed = false;
let springData = null;
let fallData = null;

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadSection = document.getElementById('upload-section');
const dataSection = document.getElementById('data-section');
const loadingOverlay = document.getElementById('loading-overlay');
const tableHeader = document.getElementById('table-header');
const tableBody = document.getElementById('table-body');
const removeRowsBtn = document.getElementById('remove-selected-rows');
const removeColumnsBtn = document.getElementById('remove-columns-btn');
const filterRowsBtn = document.getElementById('filter-rows-btn');
const keepColumnsBtn = document.getElementById('keep-columns-btn');
const transposeBtn = document.getElementById('transpose-btn');
const quickProcessBtn = document.getElementById('quick-process-btn');
const resetBtn = document.getElementById('reset-btn');
const downloadBtn = document.getElementById('download-btn');
const emailBtn = document.getElementById('email-btn');
const newUploadBtn = document.getElementById('new-upload-btn');
const columnModal = new bootstrap.Modal(document.getElementById('columnModal'));
const filterModal = new bootstrap.Modal(document.getElementById('filterModal'));
const keepColumnsModal = new bootstrap.Modal(document.getElementById('keepColumnsModal'));
const emailModal = new bootstrap.Modal(document.getElementById('emailModal'));

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
removeRowsBtn.addEventListener('click', removeSelectedRows);
removeColumnsBtn.addEventListener('click', showColumnModal);
filterRowsBtn.addEventListener('click', showFilterModal);
keepColumnsBtn.addEventListener('click', showKeepColumnsModal);
transposeBtn.addEventListener('click', transposeData);
quickProcessBtn.addEventListener('click', quickProcess);
resetBtn.addEventListener('click', resetData);
downloadBtn.addEventListener('click', downloadReport);
emailBtn.addEventListener('click', showEmailModal);
newUploadBtn.addEventListener('click', resetToUpload);
document.getElementById('confirm-remove-columns').addEventListener('click', removeSelectedColumns);
document.getElementById('confirm-filter-rows').addEventListener('click', applyFilter);
document.getElementById('confirm-keep-columns').addEventListener('click', applyKeepColumns);
document.getElementById('confirm-send-email').addEventListener('click', sendEmailReport);

// Drag and Drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// File Upload
async function uploadFile(file) {
    const validExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!validExtensions.includes(fileExtension)) {
        showAlert('Please upload a valid file (.xlsx, .xls, or .csv)', 'danger');
        return;
    }

    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            sessionId = result.session_id;
            currentData = result.data;
            currentColumns = result.columns;
            
            displayData(result);
            showDataSection();
            updateSummary();
            showAlert(`File "${file.name}" uploaded successfully!`, 'success');
        } else {
            showAlert(result.error || 'Error uploading file', 'danger');
        }
    } catch (error) {
        showAlert('Error uploading file: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Display Data in Table
function displayData(result) {
    currentData = result.data;
    currentColumns = result.columns;
    selectedRows.clear();
    updateRemoveRowsButton();
    
    // Make sure single table view is visible (for non-quick-process operations)
    document.getElementById('single-table-view').classList.remove('d-none');

    // Build header
    tableHeader.innerHTML = '<th><input type="checkbox" class="form-check-input" id="select-all"></th>' +
        '<th>#</th>' +
        currentColumns.map(col => `<th>${escapeHtml(col)}</th>`).join('');

    // Add select all functionality
    document.getElementById('select-all').addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('.row-checkbox');
        checkboxes.forEach((cb, index) => {
            cb.checked = this.checked;
            if (this.checked) {
                selectedRows.add(index);
            } else {
                selectedRows.delete(index);
            }
            updateRowSelection(index);
        });
        updateRemoveRowsButton();
    });

    // Build body
    tableBody.innerHTML = currentData.map((row, index) => {
        const cells = currentColumns.map(col => `<td title="${escapeHtml(String(row[col] || ''))}">${escapeHtml(String(row[col] || ''))}</td>`).join('');
        return `<tr data-index="${index}">
            <td><input type="checkbox" class="form-check-input row-checkbox" data-index="${index}"></td>
            <td>${index + 1}</td>
            ${cells}
        </tr>`;
    }).join('');

    // Add row click handlers
    document.querySelectorAll('.row-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const index = parseInt(this.dataset.index);
            if (this.checked) {
                selectedRows.add(index);
            } else {
                selectedRows.delete(index);
            }
            updateRowSelection(index);
            updateRemoveRowsButton();
        });
    });

    // Update stats
    document.getElementById('total-rows').textContent = result.total_rows;
    document.getElementById('total-columns').textContent = result.total_columns;
}

function updateRowSelection(index) {
    const row = document.querySelector(`tr[data-index="${index}"]`);
    if (row) {
        if (selectedRows.has(index)) {
            row.classList.add('selected');
        } else {
            row.classList.remove('selected');
        }
    }
}

function updateRemoveRowsButton() {
    removeRowsBtn.disabled = selectedRows.size === 0;
    removeRowsBtn.innerHTML = selectedRows.size > 0 
        ? `<i class="bi bi-trash me-1"></i>Remove ${selectedRows.size} Row(s)`
        : '<i class="bi bi-trash me-1"></i>Remove Selected Rows';
}

// Remove Selected Rows
async function removeSelectedRows() {
    if (selectedRows.size === 0) return;

    showLoading();

    try {
        const response = await fetch('/remove-rows', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                row_indices: Array.from(selectedRows)
            })
        });

        const result = await response.json();

        if (result.success) {
            displayData(result);
            updateSummary();
            showAlert(`${selectedRows.size} row(s) removed successfully!`, 'success');
        } else {
            showAlert(result.error || 'Error removing rows', 'danger');
        }
    } catch (error) {
        showAlert('Error removing rows: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Show Column Selection Modal
function showColumnModal() {
    const container = document.getElementById('column-checkboxes');
    container.innerHTML = currentColumns.map((col, index) => `
        <div class="form-check">
            <input class="form-check-input column-checkbox" type="checkbox" value="${escapeHtml(col)}" id="col-${index}">
            <label class="form-check-label" for="col-${index}">${escapeHtml(col)}</label>
        </div>
    `).join('');
    
    columnModal.show();
}

// Remove Selected Columns
async function removeSelectedColumns() {
    const selectedColumns = Array.from(document.querySelectorAll('.column-checkbox:checked'))
        .map(cb => cb.value);

    if (selectedColumns.length === 0) {
        showAlert('Please select at least one column to remove', 'warning');
        return;
    }

    columnModal.hide();
    showLoading();

    try {
        const response = await fetch('/remove-columns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                column_names: selectedColumns
            })
        });

        const result = await response.json();

        if (result.success) {
            displayData(result);
            updateSummary();
            showAlert(`${selectedColumns.length} column(s) removed successfully!`, 'success');
        } else {
            showAlert(result.error || 'Error removing columns', 'danger');
        }
    } catch (error) {
        showAlert('Error removing columns: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Reset Data
async function resetData() {
    if (!confirm('Are you sure you want to reset all changes?')) return;

    showLoading();

    try {
        const response = await fetch('/reset-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const result = await response.json();

        if (result.success) {
            // Switch back to single table view
            showSingleTableView();
            displayData(result);
            updateSummary();
            showAlert('Data reset to original state!', 'success');
        } else {
            showAlert(result.error || 'Error resetting data', 'danger');
        }
    } catch (error) {
        showAlert('Error resetting data: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Show single table view (hide split view)
function showSingleTableView() {
    isSplitView = false;
    isTransposed = false;
    springData = null;
    fallData = null;
    document.getElementById('single-table-view').classList.remove('d-none');
    document.getElementById('split-table-view').classList.add('d-none');
}

// Update Summary
async function updateSummary() {
    try {
        const response = await fetch('/get-summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const summary = await response.json();

        document.getElementById('total-rows').textContent = summary.current_rows;
        document.getElementById('total-columns').textContent = summary.current_columns;
        document.getElementById('rows-removed').textContent = summary.rows_removed;
        document.getElementById('columns-removed').textContent = summary.columns_removed;
    } catch (error) {
        console.error('Error updating summary:', error);
    }
}

// Download Report
async function downloadReport() {
    showLoading();

    try {
        const response = await fetch('/download-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId,
                split_view: isSplitView,
                transposed: isTransposed
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'report_modified.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            showAlert('Report downloaded successfully!', 'success');
        } else {
            const result = await response.json();
            showAlert(result.error || 'Error downloading report', 'danger');
        }
    } catch (error) {
        showAlert('Error downloading report: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// UI Helpers
function showDataSection() {
    uploadSection.classList.add('d-none');
    dataSection.classList.remove('d-none');
}

function resetToUpload() {
    sessionId = null;
    currentData = [];
    currentColumns = [];
    selectedRows.clear();
    fileInput.value = '';
    
    uploadSection.classList.remove('d-none');
    dataSection.classList.add('d-none');
}

function showLoading() {
    loadingOverlay.classList.remove('d-none');
}

function hideLoading() {
    loadingOverlay.classList.add('d-none');
}

function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = alertHtml;
    alertContainer.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
    document.body.appendChild(alertContainer);
    
    setTimeout(() => {
        alertContainer.remove();
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show Filter Modal
function showFilterModal() {
    const select = document.getElementById('filter-column-select');
    select.innerHTML = '<option value="">-- Select a column --</option>' +
        currentColumns.map(col => `<option value="${escapeHtml(col)}">${escapeHtml(col)}</option>`).join('');
    
    // Pre-fill with commonly used program names
    const defaultValues = `Woodhaven
Marietta
San Clemente
Rosemont
Pullenvale
Minos
Misawa
Fernvale`;
    document.getElementById('filter-values-input').value = defaultValues;
    filterModal.show();
}

// Apply Filter
async function applyFilter() {
    const columnName = document.getElementById('filter-column-select').value;
    const valuesText = document.getElementById('filter-values-input').value;
    
    if (!columnName) {
        showAlert('Please select a column to filter', 'warning');
        return;
    }
    
    if (!valuesText.trim()) {
        showAlert('Please enter values to filter by', 'warning');
        return;
    }
    
    // Parse values - split by newlines and commas, then trim
    const filterValues = valuesText
        .split(/[\n,]+/)
        .map(v => v.trim())
        .filter(v => v.length > 0);
    
    if (filterValues.length === 0) {
        showAlert('Please enter at least one value to filter by', 'warning');
        return;
    }
    
    filterModal.hide();
    showLoading();

    try {
        const response = await fetch('/filter-rows', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                column_name: columnName,
                filter_values: filterValues
            })
        });

        const result = await response.json();

        if (result.success) {
            displayData(result);
            updateSummary();
            showAlert(`Filter applied! Kept ${result.rows_kept} rows, removed ${result.rows_removed} rows.`, 'success');
        } else {
            showAlert(result.error || 'Error applying filter', 'danger');
        }
    } catch (error) {
        showAlert('Error applying filter: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Show Keep Columns Modal
function showKeepColumnsModal() {
    // Pre-fill with commonly used columns
    const defaultColumns = `Program
BCR
BOP
ASR
EV1 BB Vol
DCR and CRB
EV2 BB Vol
EMV
DV BB Vol
DVR
Mfg Build  Start
SW - PQBIH
PQ_RTM
SW - RTM
PQS
SW - RTP BIH
Ready to Sell`;
    document.getElementById('keep-columns-input').value = defaultColumns;
    keepColumnsModal.show();
}

// Apply Keep Columns
async function applyKeepColumns() {
    const columnsText = document.getElementById('keep-columns-input').value;
    
    if (!columnsText.trim()) {
        showAlert('Please enter column names to keep', 'warning');
        return;
    }
    
    // Parse column names - split by newlines, then trim
    const columnsToKeep = columnsText
        .split(/[\n]+/)
        .map(v => v.trim())
        .filter(v => v.length > 0);
    
    if (columnsToKeep.length === 0) {
        showAlert('Please enter at least one column name to keep', 'warning');
        return;
    }
    
    keepColumnsModal.hide();
    showLoading();

    try {
        const response = await fetch('/keep-columns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                column_names: columnsToKeep
            })
        });

        const result = await response.json();

        if (result.success) {
            displayData(result);
            updateSummary();
            showAlert(`Kept ${result.columns_kept} columns. All other columns removed.`, 'success');
        } else {
            showAlert(result.error || 'Error keeping columns', 'danger');
        }
    } catch (error) {
        showAlert('Error keeping columns: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Transpose Data (swap rows and columns)
async function transposeData() {
    showLoading();

    try {
        // If in split view mode, transpose both tables
        if (isSplitView) {
            const response = await fetch('/transpose-split', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            const result = await response.json();

            if (result.success) {
                isTransposed = true;
                springData = result.spring_2026;
                fallData = result.fall_2026;
                displaySplitViewTransposed(result);
                updateSummary();
                showAlert(`Data transposed! Spring: ${result.spring_2026.total_rows} rows, Fall: ${result.fall_2026.total_rows} rows.`, 'success');
            } else {
                showAlert(result.error || 'Error transposing data', 'danger');
            }
        } else {
            const response = await fetch('/transpose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            const result = await response.json();

            if (result.success) {
                displayData(result);
                updateSummary();
                showAlert(`Data transposed! Now ${result.total_rows} rows and ${result.total_columns} columns.`, 'success');
            } else {
                showAlert(result.error || 'Error transposing data', 'danger');
            }
        }
    } catch (error) {
        showAlert('Error transposing data: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Display Split View Transposed
function displaySplitViewTransposed(result) {
    // Build Spring 2026 table
    const springHeader = document.getElementById('spring-table-header');
    const springBody = document.getElementById('spring-table-body');
    
    springHeader.innerHTML = '<th>#</th>' +
        result.spring_2026.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('');
    
    springBody.innerHTML = result.spring_2026.data.map((row, index) => {
        const cells = result.spring_2026.columns.map(col => `<td title="${escapeHtml(String(row[col] || ''))}">${escapeHtml(String(row[col] || ''))}</td>`).join('');
        return `<tr><td>${index + 1}</td>${cells}</tr>`;
    }).join('');
    
    // Build Fall 2026 table
    const fallHeader = document.getElementById('fall-table-header');
    const fallBody = document.getElementById('fall-table-body');
    
    fallHeader.innerHTML = '<th>#</th>' +
        result.fall_2026.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('');
    
    fallBody.innerHTML = result.fall_2026.data.map((row, index) => {
        const cells = result.fall_2026.columns.map(col => `<td title="${escapeHtml(String(row[col] || ''))}">${escapeHtml(String(row[col] || ''))}</td>`).join('');
        return `<tr><td>${index + 1}</td>${cells}</tr>`;
    }).join('');
}

// Show Email Modal
function showEmailModal() {
    emailModal.show();
}

// Send Email Report
async function sendEmailReport() {
    const email = document.getElementById('email-input').value.trim();
    
    if (!email) {
        showAlert('Please enter an email address', 'warning');
        return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showAlert('Please enter a valid email address', 'warning');
        return;
    }
    
    emailModal.hide();
    showLoading();

    try {
        const response = await fetch('/email-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                email: email
            })
        });

        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');
        } else {
            showAlert(result.error || 'Error sending email', 'danger');
        }
    } catch (error) {
        showAlert('Error sending email: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Quick Process - Do everything in one click
async function quickProcess() {
    showLoading();

    try {
        const response = await fetch('/quick-process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId
            })
        });

        const result = await response.json();

        if (result.success) {
            displayData(result);
            
            // Check if we should show split view
            if (result.split_view && result.spring_2026 && result.fall_2026) {
                isSplitView = true;
                springData = result.spring_2026;
                fallData = result.fall_2026;
                displaySplitView(result);
            }
            
            updateSummary();
            showAlert(`Quick Process complete! Data now has ${result.total_rows} rows and ${result.total_columns} columns.`, 'success');
        } else {
            showAlert(result.error || 'Error processing data', 'danger');
        }
    } catch (error) {
        showAlert('Error processing data: ' + error.message, 'danger');
    } finally {
        hideLoading();
    }
}

// Display Split View - Spring 2026 and Fall 2026 tables
function displaySplitView(result) {
    // Hide single table view, show split view
    document.getElementById('single-table-view').classList.add('d-none');
    document.getElementById('split-table-view').classList.remove('d-none');
    
    const springData = result.spring_2026;
    const fallData = result.fall_2026;
    
    // Build Spring 2026 table
    const springHeader = document.getElementById('spring-table-header');
    const springBody = document.getElementById('spring-table-body');
    
    springHeader.innerHTML = '<th>#</th>' +
        springData.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('');
    
    springBody.innerHTML = springData.data.map((row, index) => {
        const cells = springData.columns.map(col => `<td title="${escapeHtml(String(row[col] || ''))}">${escapeHtml(String(row[col] || ''))}</td>`).join('');
        return `<tr><td>${index + 1}</td>${cells}</tr>`;
    }).join('');
    
    // Build Fall 2026 table
    const fallHeader = document.getElementById('fall-table-header');
    const fallBody = document.getElementById('fall-table-body');
    
    fallHeader.innerHTML = '<th>#</th>' +
        fallData.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('');
    
    fallBody.innerHTML = fallData.data.map((row, index) => {
        const cells = fallData.columns.map(col => `<td title="${escapeHtml(String(row[col] || ''))}">${escapeHtml(String(row[col] || ''))}</td>`).join('');
        return `<tr><td>${index + 1}</td>${cells}</tr>`;
    }).join('');
}
