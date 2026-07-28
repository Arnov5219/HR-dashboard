
    // State storage for Fetch updates
    const todayState = {
        page: 1,
        limit: 25,
        sort_col: 'employee_name',
        sort_dir: 'asc',
        search: '',
        employee_ids: [],
        months: [],
        weeks: []
    };

    const historyState = {
        page: 1,
        limit: 25,
        sort_col: 'date',
        sort_dir: 'desc',
        search: '',
        employee_ids: [],
        months: [],
        weeks: [],
        dates: [], // specific date filters
        date_range: 'last_7_days',
        start_date: '',
        end_date: ''
    };

    // Initial page load
    document.addEventListener("DOMContentLoaded", () => {
        // Load initial values for dropdown filters
        loadFilterDropdowns();
        
        // Refresh attendance tables
        refreshAllData();
        
        // Silent background sync every 5 seconds
        setInterval(refreshAllData, 5000);
    });

    function refreshAllData() {
        loadTodayTable();
        loadHistoryTable();
    }

    // Fetch column options (employees, dates, etc.) and build dropdown checklists
    async function loadFilterDropdowns() {
        try {
            const res = await fetch('/api/filters/');
            const data = await res.json();
            
            // 1. Employee Multiselect Filter (main toolbar)
            const empListDiv = document.getElementById('employeeList');
            empListDiv.innerHTML = '';
            data.employees.forEach(emp => {
                const item = document.createElement('div');
                item.className = 'form-check filter-list-item-node';
                item.innerHTML = `
                    <input class="form-check-input employee-filter-checkbox" type="checkbox" value="${emp.id}" id="emp-check-${emp.id}" checked onchange="onEmployeeFilterChange()">
                    <label class="form-check-label" for="emp-check-${emp.id}">${emp.name} (${emp.id})</label>
                `;
                empListDiv.appendChild(item);
            });
            
            // 1b. Month Multiselect Filter (main toolbar)
            const monthListDiv = document.getElementById('monthList');
            monthListDiv.innerHTML = '';
            data.months.forEach(m => {
                const item = document.createElement('div');
                item.className = 'form-check filter-list-item-node';
                item.innerHTML = `
                    <input class="form-check-input month-filter-checkbox" type="checkbox" value="${m}" id="month-check-${m.replace(/\s+/g, '-')}" checked onchange="onMonthFilterChange()">
                    <label class="form-check-label" for="month-check-${m.replace(/\s+/g, '-')}">${m}</label>
                `;
                monthListDiv.appendChild(item);
            });

            // 1c. Week Multiselect Filter (main toolbar)
            const weekListDiv = document.getElementById('weekList');
            weekListDiv.innerHTML = '';
            data.weeks.forEach(w => {
                const item = document.createElement('div');
                item.className = 'form-check filter-list-item-node';
                item.innerHTML = `
                    <input class="form-check-input week-filter-checkbox" type="checkbox" value="${w}" id="week-check-${w.replace(/\s+/g, '-')}" checked onchange="onWeekFilterChange()">
                    <label class="form-check-label" for="week-check-${w.replace(/\s+/g, '-')}">${w}</label>
                `;
                weekListDiv.appendChild(item);
            });
            
            // 2. Today Table column checklists
            populateHeaderChecklist('today', 'employee_id', data.employees.map(e => ({ val: e.id, label: e.id })));
            populateHeaderChecklist('today', 'employee_name', data.employees.map(e => ({ val: e.name, label: e.name })));
            
            // 3. History Table column checklists
            populateHeaderChecklist('history', 'employee_id', data.employees.map(e => ({ val: e.id, label: e.id })));
            populateHeaderChecklist('history', 'employee_name', data.employees.map(e => ({ val: e.name, label: e.name })));
            
            // 4. Date Hierarchical Checklist (Excel-like tree in History Date Header)
            buildDateHierarchy(data.dates);
            
        } catch (err) {
            console.error("Failed to load filter choices:", err);
        }
    }

    // Populate standard checkbox checklists inside column headers
    function populateHeaderChecklist(tableName, filterField, items) {
        const lists = document.querySelectorAll(`.filter-list[data-filter="${filterField}"][data-table="${tableName}"]`);
        lists.forEach(listDiv => {
            listDiv.innerHTML = '';
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'filter-list-item';
                div.innerHTML = `
                    <input type="checkbox" value="${item.val}" checked onchange="onColumnCheckboxChange('${tableName}', '${filterField}')">
                    <span>${item.label}</span>
                `;
                listDiv.appendChild(div);
            });
        });
    }

    // Build Excel-like Hierarchical Date Tree
    function buildDateHierarchy(yearsTree) {
        const container = document.getElementById('dateHierarchyFilterList');
        container.innerHTML = '';
        
        Object.keys(yearsTree).sort((a,b)=>b-a).forEach(yr => {
            const yrId = `yr-${yr}`;
            const yrDiv = document.createElement('div');
            yrDiv.className = 'hierarchy-root mb-1';
            
            yrDiv.innerHTML = `
                <div class="d-flex align-items-center gap-1">
                    <span class="hierarchy-toggle text-secondary" onclick="toggleCollapse('${yrId}')"><i class="fa-solid fa-chevron-down" id="toggle-icon-${yrId}"></i></span>
                    <input type="checkbox" checked class="date-node-check" data-level="year" data-value="${yr}" onchange="toggleHierarchyCheckboxes(this)">
                    <span class="fw-bold">${yr}</span>
                </div>
                <div class="hierarchy-node" id="${yrId}"></div>
            `;
            container.appendChild(yrDiv);
            
            const yrNode = document.getElementById(yrId);
            
            Object.keys(yearsTree[yr]).forEach(mName => {
                const mIdx = getMonthIndexFromName(mName); // Returns index (1-12)
                const mCode = `${yr}-${mIdx.toString().padStart(2, '0')}`;
                const mId = `m-${mCode}`;
                const mDiv = document.createElement('div');
                mDiv.className = 'mb-1';
                
                mDiv.innerHTML = `
                    <div class="d-flex align-items-center gap-1">
                        <span class="hierarchy-toggle text-secondary" onclick="toggleCollapse('${mId}')"><i class="fa-solid fa-chevron-down" id="toggle-icon-${mId}"></i></span>
                        <input type="checkbox" checked class="date-node-check" data-level="month" data-value="${mCode}" onchange="toggleHierarchyCheckboxes(this)">
                        <span>${mName}</span>
                    </div>
                    <div class="hierarchy-node" id="${mId}"></div>
                `;
                yrNode.appendChild(mDiv);
                
                const mNode = document.getElementById(mId);
                
                yearsTree[yr][mName].sort((a,b)=>b-a).forEach(day => {
                    const dCode = `${mCode}-${day.toString().padStart(2, '0')}`;
                    const dDiv = document.createElement('div');
                    dDiv.className = 'd-flex align-items-center gap-1 py-0.5';
                    
                    dDiv.innerHTML = `
                        <input type="checkbox" value="${dCode}" checked class="date-node-check date-leaf-checkbox" data-level="day" onchange="onDateLeafChange()">
                        <span class="text-secondary">${day.toString().padStart(2, '0')}</span>
                    `;
                    mNode.appendChild(dDiv);
                });
            });
        });
    }

    // Toggle collapse in tree structure
    function toggleCollapse(nodeId) {
        const div = document.getElementById(nodeId);
        const icon = document.getElementById(`toggle-icon-${nodeId}`);
        if (div.classList.contains('d-none')) {
            div.classList.remove('d-none');
            icon.className = 'fa-solid fa-chevron-down';
        } else {
            div.classList.add('d-none');
            icon.className = 'fa-solid fa-chevron-right';
        }
    }

    // Checking/unchecking year or month checks all children
    function toggleHierarchyCheckboxes(el) {
        const level = el.getAttribute('data-level');
        const val = el.getAttribute('data-value');
        const checked = el.checked;
        
        let selector = '';
        if (level === 'year') {
            selector = `input[data-value^="${val}"]`;
            // Also select leaves (days) under that year
            const yearNode = el.closest('.hierarchy-root').querySelector('.hierarchy-node');
            const dayCheckboxes = yearNode.querySelectorAll('.date-leaf-checkbox');
            dayCheckboxes.forEach(cb => cb.checked = checked);
        } else if (level === 'month') {
            selector = `input[data-value="${val}"]`;
            // Select leaves under that month
            const parentDiv = el.closest('div').nextElementSibling;
            const dayCheckboxes = parentDiv.querySelectorAll('.date-leaf-checkbox');
            dayCheckboxes.forEach(cb => cb.checked = checked);
        }
        
        const children = el.closest('.hierarchy-root').querySelectorAll(selector);
        children.forEach(child => child.checked = checked);
        
        onDateLeafChange();
    }

    // Helper month mapper
    function getMonthIndexFromName(name) {
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        return months.indexOf(name) + 1;
    }

    // Trigger history reload when hierarchical date leaf changed
    function onDateLeafChange() {
        const checkedLeaves = document.querySelectorAll('.date-leaf-checkbox:checked');
        const dates = Array.from(checkedLeaves).map(cb => cb.value);
        
        historyState.dates = dates;
        historyState.page = 1;
        loadHistoryTable();
    }

    // Filter checkbox items in column header dropdowns
    function filterCheckboxes(inputEl) {
        const text = inputEl.value.toLowerCase();
        const items = inputEl.nextElementSibling.nextElementSibling.querySelectorAll('.filter-list-item');
        items.forEach(item => {
            const label = item.querySelector('span').innerText.toLowerCase();
            if (label.includes(text)) {
                item.classList.remove('d-none');
            } else {
                item.classList.add('d-none');
            }
        });
    }

    // Toggle checklists (Select All checkbox in dropdown)
    function toggleCheckboxes(selectAllEl) {
        const checked = selectAllEl.checked;
        const listDiv = selectAllEl.parentElement.nextElementSibling;
        const checkboxes = listDiv.querySelectorAll('input[type="checkbox"]');
        
        checkboxes.forEach(cb => {
            if (!cb.parentElement.classList.contains('d-none')) {
                cb.checked = checked;
            }
        });
        
        const table = listDiv.getAttribute('data-table');
        const filter = listDiv.getAttribute('data-filter');
        onColumnCheckboxChange(table, filter);
    }

    // Handle column filter checklist toggle
    function onColumnCheckboxChange(tableName, filterField) {
        const lists = document.querySelectorAll(`.filter-list[data-filter="${filterField}"][data-table="${tableName}"]`);
        let selected = [];
        
        // Loop and get unchecked items to see what was filtered out
        const checkedBoxes = lists[0].querySelectorAll('input[type="checkbox"]:checked');
        const totalBoxes = lists[0].querySelectorAll('input[type="checkbox"]');
        
        selected = Array.from(checkedBoxes).map(cb => cb.value);
        
        // If all selected, pass empty array to backend (means no filter/select all)
        const activeFilter = (checkedBoxes.length === totalBoxes.length) ? [] : selected;
        
        if (tableName === 'today') {
            if (filterField === 'employee_id' || filterField === 'employee_name') {
                todayState.employee_ids = activeFilter;
            }
            todayState.page = 1;
            loadTodayTable();
        } else {
            if (filterField === 'employee_id' || filterField === 'employee_name') {
                historyState.employee_ids = activeFilter;
            }
            historyState.page = 1;
            loadHistoryTable();
        }
    }

    // Search bar helper (Main employee select checklist)
    function filterDropdownList(listId, val) {
        const text = val.toLowerCase();
        const items = document.getElementById(listId).querySelectorAll('.filter-list-item-node');
        items.forEach(item => {
            const label = item.querySelector('label').innerText.toLowerCase();
            if (label.includes(text)) {
                item.classList.remove('d-none');
            } else {
                item.classList.add('d-none');
            }
        });
    }

    // Toggle main filter checklists
    function toggleDropdownSelectAll(listId, checked) {
        let cbClass = '';
        let changeFn = null;
        if (listId === 'employeeList') {
            cbClass = '.employee-filter-checkbox';
            changeFn = onEmployeeFilterChange;
        } else if (listId === 'monthList') {
            cbClass = '.month-filter-checkbox';
            changeFn = onMonthFilterChange;
        } else if (listId === 'weekList') {
            cbClass = '.week-filter-checkbox';
            changeFn = onWeekFilterChange;
        }
        
        const items = document.getElementById(listId).querySelectorAll(cbClass);
        items.forEach(item => {
            if (!item.parentElement.classList.contains('d-none')) {
                item.checked = checked;
            }
        });
        if (changeFn) changeFn();
    }

    // Employee Filter toolbar change
    function onEmployeeFilterChange() {
        const checkBoxes = document.querySelectorAll('.employee-filter-checkbox:checked');
        const totalBoxes = document.querySelectorAll('.employee-filter-checkbox');
        
        const selected = Array.from(checkBoxes).map(cb => cb.value);
        const activeFilter = (checkBoxes.length === totalBoxes.length) ? [] : selected;
        
        // Sync to both tables
        todayState.employee_ids = activeFilter;
        historyState.employee_ids = activeFilter;
        
        todayState.page = 1;
        historyState.page = 1;
        
        loadTodayTable();
        loadHistoryTable();
    }

    // Month Filter toolbar change
    function onMonthFilterChange() {
        const checkBoxes = document.querySelectorAll('.month-filter-checkbox:checked');
        const totalBoxes = document.querySelectorAll('.month-filter-checkbox');
        
        const selected = Array.from(checkBoxes).map(cb => cb.value);
        const activeFilter = (checkBoxes.length === totalBoxes.length) ? [] : selected;
        
        todayState.months = activeFilter;
        historyState.months = activeFilter;
        
        todayState.page = 1;
        historyState.page = 1;
        
        loadTodayTable();
        loadHistoryTable();
    }

    // Week Filter toolbar change
    function onWeekFilterChange() {
        const checkBoxes = document.querySelectorAll('.week-filter-checkbox:checked');
        const totalBoxes = document.querySelectorAll('.week-filter-checkbox');
        
        const selected = Array.from(checkBoxes).map(cb => cb.value);
        const activeFilter = (checkBoxes.length === totalBoxes.length) ? [] : selected;
        
        todayState.weeks = activeFilter;
        historyState.weeks = activeFilter;
        
        todayState.page = 1;
        historyState.page = 1;
        
        loadTodayTable();
        loadHistoryTable();
    }

    // Global Search trigger
    let searchTimeout = null;
    function onGlobalSearch(query) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            todayState.search = query;
            historyState.search = query;
            
            todayState.page = 1;
            historyState.page = 1;
            
            loadTodayTable();
            loadHistoryTable();
        }, 300);
    }

    // Date range selector for History table
    function setHistoryDateRange(range) {
        historyState.date_range = range;
        
        const customDiv = document.getElementById('custom-date-inputs');
        if (range === 'custom') {
            customDiv.classList.remove('d-none');
            customDiv.classList.add('d-flex');
        } else {
            customDiv.classList.remove('d-flex');
            customDiv.classList.add('d-none');
        }
        
        historyState.page = 1;
        loadHistoryTable();
    }

    // Sort column headers
    function sortTable(tableType, colName, direction) {
        if (tableType === 'today') {
            todayState.sort_col = colName;
            todayState.sort_dir = direction;
            todayState.page = 1;
            loadTodayTable();
        } else {
            historyState.sort_col = colName;
            historyState.sort_dir = direction;
            historyState.page = 1;
            loadHistoryTable();
        }
    }

    // Page switches
    function changePage(tableType, page) {
        if (tableType === 'today') {
            todayState.page = page;
            loadTodayTable();
        } else {
            historyState.page = page;
            loadHistoryTable();
        }
    }

    // Build endpoint query URL string
    function buildQueryString(state) {
        let params = new URLSearchParams();
        params.append('page', state.page);
        params.append('limit', state.limit);
        if (state.sort_col) {
            params.append('sort_col', state.sort_col);
            params.append('sort_dir', state.sort_dir);
        }
        if (state.search) {
            params.append('search', state.search);
        }
        if (state.employee_ids && state.employee_ids.length > 0) {
            params.append('employees', state.employee_ids.join(','));
        }
        if (state.months && state.months.length > 0) {
            params.append('months', state.months.join(','));
        }
        if (state.weeks && state.weeks.length > 0) {
            params.append('weeks', state.weeks.join(','));
        }
        if (state.date_range) {
            params.append('date_range', state.date_range);
        }
        if (state.date_range === 'custom') {
            const start = document.getElementById('history-start-date').value;
            const end = document.getElementById('history-end-date').value;
            params.append('start_date', start);
            params.append('end_date', end);
        }
        if (state.dates && state.dates.length > 0) {
            params.append('dates', state.dates.join(','));
            params.append('date_range', 'selected_dates');
        }
        return params.toString();
    }

    // Dynamic Today's table renderer
    async function loadTodayTable() {
        const overlay = document.getElementById('loading-today');
        overlay.classList.add('active');
        
        try {
            const query = buildQueryString(todayState);
            const res = await fetch(`/api/attendance/today/?${query}`);
            const data = await res.json();
            
            const tbody = document.getElementById('today-table-body');
            tbody.innerHTML = '';
            
            if (data.records.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-5 text-muted">
                            <i class="fa-solid fa-inbox fs-2 d-block mb-2"></i>
                            No attendance records found for today.
                        </td>
                    </tr>
                `;
            } else {
                data.records.forEach(r => {
                    const row = document.createElement('tr');
                    
                    row.innerHTML = `
                        <td class="fw-bold">${r.employee_id}</td>
                        <td class="fw-bold text-primary">${r.employee_name}</td>
                        <td class="text-secondary">${r.date}</td>
                        <td>${r.in_time ? `<span class="badge bg-light text-dark border font-monospace">${r.in_time}</span>` : '<span class="text-muted">-</span>'}</td>
                        <td>${r.out_time ? `<span class="badge bg-light text-dark border font-monospace">${r.out_time}</span>` : '<span class="text-muted">-</span>'}</td>
                        <td>${r.total_hours ? `<span class="badge bg-light text-dark border font-monospace">${r.total_hours}</span>` : '<span class="text-muted">-</span>'}</td>
                    `;
                    tbody.appendChild(row);
                });
            }
            
            document.getElementById('today-table-info').innerText = data.total_count === 1 ? '1 entry' : `${data.total_count} entries`;
            
            renderPagination('today', data.page, data.pages);
            
        } catch (err) {
            console.error("Failed to load today's attendance table:", err);
        } finally {
            overlay.classList.remove('active');
        }
    }

    // Dynamic History table renderer
    async function loadHistoryTable() {
        const overlay = document.getElementById('loading-history');
        overlay.classList.add('active');
        
        try {
            const query = buildQueryString(historyState);
            const res = await fetch(`/api/attendance/history/?${query}`);
            const data = await res.json();
            
            const tbody = document.getElementById('history-table-body');
            tbody.innerHTML = '';
            
            if (data.records.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-5 text-muted">
                            <i class="fa-solid fa-inbox fs-2 d-block mb-2"></i>
                            No historical records found matching filter states.
                        </td>
                    </tr>
                `;
            } else {
                data.records.forEach(r => {
                    const row = document.createElement('tr');
                    
                    row.innerHTML = `
                        <td>${r.employee_id}</td>
                        <td class="text-primary fw-medium">${r.employee_name}</td>
                        <td>${r.date}</td>
                        <td>${r.in_time ? `<span class="badge bg-light text-dark border font-monospace">${r.in_time}</span>` : '<span class="text-muted">-</span>'}</td>
                        <td>${r.out_time ? `<span class="badge bg-light text-dark border font-monospace">${r.out_time}</span>` : '<span class="text-muted">-</span>'}</td>
                        <td>${r.total_hours ? `<span class="badge bg-light text-dark border font-monospace">${r.total_hours}</span>` : '<span class="text-muted">-</span>'}</td>
                    `;
                    tbody.appendChild(row);
                });
            }
            
            document.getElementById('history-table-info').innerText = data.total_count === 1 ? '1 entry' : `${data.total_count} entries`;
            
            renderPagination('history', data.page, data.pages);
            
        } catch (err) {
            console.error("Failed to load historical attendance table:", err);
        } finally {
            overlay.classList.remove('active');
        }
    }

    // Build pagination links
    function renderPagination(tableType, currentPage, totalPages) {
        const pag = document.getElementById(`${tableType}-pagination`);
        pag.innerHTML = '';
        
        if (totalPages <= 1) return;
        
        // Prev button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" onclick="changePage('${tableType}', ${currentPage - 1}); return false;"><i class="fa-solid fa-angle-left"></i></a>`;
        pag.appendChild(prevLi);
        
        // Range logic
        const maxPagesToShow = 5;
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
        if (endPage - startPage < maxPagesToShow - 1) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${currentPage === i ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#" onclick="changePage('${tableType}', ${i}); return false;">${i}</a>`;
            pag.appendChild(li);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" onclick="changePage('${tableType}', ${currentPage + 1}); return false;"><i class="fa-solid fa-angle-right"></i></a>`;
        pag.appendChild(nextLi);
    }

    // Reset all filters in toolbar and column headers back to default state
    function resetAllFilters() {
        // 1. Reset Global Search
        document.getElementById('global-search').value = '';
        todayState.search = '';
        historyState.search = '';
        
        // 2. Reset Employee Multiselect Filter
        todayState.employee_ids = [];
        historyState.employee_ids = [];
        document.querySelectorAll('.employee-filter-checkbox').forEach(cb => cb.checked = true);
        const empSelectAll = document.getElementById('employeeSelectAll');
        if (empSelectAll) empSelectAll.checked = true;
        
        // 3. Reset Month Multiselect Filter
        todayState.months = [];
        historyState.months = [];
        document.querySelectorAll('.month-filter-checkbox').forEach(cb => cb.checked = true);
        const monthSelectAll = document.getElementById('monthSelectAll');
        if (monthSelectAll) monthSelectAll.checked = true;
        
        // 4. Reset Week Multiselect Filter
        todayState.weeks = [];
        historyState.weeks = [];
        document.querySelectorAll('.week-filter-checkbox').forEach(cb => cb.checked = true);
        const weekSelectAll = document.getElementById('weekSelectAll');
        if (weekSelectAll) weekSelectAll.checked = true;
        
        // 5. Reset Column-Header checklists
        document.querySelectorAll('.filter-list input[type="checkbox"]').forEach(cb => cb.checked = true);
        document.querySelectorAll('.select-all-check').forEach(cb => cb.checked = true);
        
        // 6. Reset Date range selector
        historyState.date_range = 'last_7_days';
        historyState.dates = [];
        historyState.start_date = '';
        historyState.end_date = '';
        
        const rangeSelect = document.getElementById('history-date-range-select');
        if (rangeSelect) rangeSelect.value = 'last_7_days';
        
        const customDiv = document.getElementById('custom-date-inputs');
        if (customDiv) {
            customDiv.classList.remove('d-flex');
            customDiv.classList.add('d-none');
        }
        
        // 7. Reset Date tree checkboxes
        document.querySelectorAll('.date-node-check').forEach(cb => cb.checked = true);
        
        // 8. Reset Pagination Pages & Reload
        todayState.page = 1;
        historyState.page = 1;
        
        loadTodayTable();
        loadHistoryTable();
    }
