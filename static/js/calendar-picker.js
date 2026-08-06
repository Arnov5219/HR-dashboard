function formatDateLocal(dateObj) {
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

class CalendarPicker {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.selectedDates = new Set(options.selectedDates || []);
        this.availableDates = new Set(options.availableDates || []);
        this.multiSelect = options.multiSelect !== false; // defaults to true
        
        let defaultDate = new Date();
        if (this.selectedDates.size > 0) {
            defaultDate = new Date([...this.selectedDates][0] + 'T00:00:00');
        } else if (this.availableDates.size > 0) {
            const sortedDates = [...this.availableDates].sort();
            defaultDate = new Date(sortedDates[sortedDates.length - 1] + 'T00:00:00');
        }
        
        this.currentYear = defaultDate.getFullYear();
        this.currentMonth = defaultDate.getMonth();
        
        this.onSelect = options.onSelect || (() => {});
        this.onClear = options.onClear || (() => {});
        
        this.months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];
        
        this.init();
    }
    
    init() {
        this.container.innerHTML = `
            <div class="calendar-container" onclick="event.stopPropagation()">
                <div class="calendar-header">
                    <div class="calendar-title-wrapper">
                        <div class="calendar-title" id="cal-month-year-title">
                            <span id="cal-month-year-text">Month, Year</span>
                            <i class="fa-solid fa-caret-down fs-8 ms-1"></i>
                        </div>
                        <div class="calendar-month-year-popover" id="cal-popover"></div>
                    </div>
                    <div class="calendar-arrows">
                        <button class="calendar-arrow-btn" type="button" id="cal-prev" title="Previous Month">↑</button>
                        <button class="calendar-arrow-btn" type="button" id="cal-next" title="Next Month">↓</button>
                    </div>
                </div>
                <div class="calendar-weekdays">
                    <div>Su</div><div>Mo</div><div>Tu</div><div>We</div><div>Th</div><div>Fr</div><div>Sa</div>
                </div>
                <div class="calendar-grid" id="cal-days-grid"></div>
                <div class="calendar-footer">
                    <button class="calendar-footer-btn clear" type="button" id="cal-clear">Clear</button>
                    ${this.multiSelect ? `<button class="calendar-footer-btn select" type="button" id="cal-submit">Select</button>` : ''}
                </div>
            </div>
        `;
        
        this.titleElement = this.container.querySelector('#cal-month-year-title');
        this.titleText = this.container.querySelector('#cal-month-year-text');
        this.popoverElement = this.container.querySelector('#cal-popover');
        this.daysGrid = this.container.querySelector('#cal-days-grid');
        
        this.setupGeneralEvents();
        this.updateCalendar();
    }
    
    setupGeneralEvents() {
        this.container.querySelector('#cal-prev').addEventListener('click', (e) => {
            e.stopPropagation();
            this.navigateMonth(-1);
        });
        this.container.querySelector('#cal-next').addEventListener('click', (e) => {
            e.stopPropagation();
            this.navigateMonth(1);
        });
        
        this.titleElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.togglePopover();
        });
        
        this.container.querySelector('#cal-clear').addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectedDates.clear();
            this.updateCalendar();
            this.onClear();
        });
        
        if (this.multiSelect) {
            this.container.querySelector('#cal-submit').addEventListener('click', (e) => {
                e.stopPropagation();
                this.onSelect(this.selectedDates);
                
                const dropdownEl = this.container.closest('.dropdown');
                if (dropdownEl) {
                    const toggleBtn = dropdownEl.querySelector('.dropdown-toggle');
                    if (toggleBtn) {
                        const dropdown = bootstrap.Dropdown.getInstance(toggleBtn) || new bootstrap.Dropdown(toggleBtn);
                        dropdown.hide();
                    }
                }
            });
        }
        
        document.addEventListener('click', () => {
            if (this.popoverElement) {
                this.popoverElement.classList.remove('show');
            }
        });
    }
    
    navigateMonth(direction) {
        this.currentMonth += direction;
        if (this.currentMonth < 0) {
            this.currentMonth = 11;
            this.currentYear -= 1;
        } else if (this.currentMonth > 11) {
            this.currentMonth = 0;
            this.currentYear += 1;
        }
        this.updateCalendar();
    }
    
    togglePopover() {
        this.popoverElement.classList.toggle('show');
        if (this.popoverElement.classList.contains('show')) {
            this.renderPopover();
        }
    }
    
    renderPopover() {
        this.popoverElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2" onclick="event.stopPropagation()">
                <button class="btn btn-sm btn-light p-1 popover-year-btn" type="button" id="pop-year-prev">&larr;</button>
                <input class="popover-year-input fw-semibold" type="number" id="pop-year-input" min="2000" max="2100" value="${this.currentYear}">
                <button class="btn btn-sm btn-light p-1 popover-year-btn" type="button" id="pop-year-next">&rarr;</button>
            </div>
            <div class="popover-grid">
                ${this.months.map((m, idx) => `
                    <div class="popover-item ${idx === this.currentMonth ? 'active' : ''}" data-month="${idx}">
                        ${m.slice(0, 3)}
                    </div>
                `).join('')}
            </div>
        `;
        
        const yearInput = this.popoverElement.querySelector('#pop-year-input');
        yearInput.addEventListener('change', (e) => {
            const val = parseInt(e.target.value);
            if (val >= 2000 && val <= 2100) {
                this.currentYear = val;
                this.updateCalendar();
            }
        });
        
        this.popoverElement.querySelector('#pop-year-prev').addEventListener('click', (e) => {
            e.stopPropagation();
            this.currentYear -= 1;
            yearInput.value = this.currentYear;
            this.updateCalendar();
        });
        
        this.popoverElement.querySelector('#pop-year-next').addEventListener('click', (e) => {
            e.stopPropagation();
            this.currentYear += 1;
            yearInput.value = this.currentYear;
            this.updateCalendar();
        });
        
        this.popoverElement.querySelectorAll('.popover-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                this.currentMonth = parseInt(item.dataset.month);
                this.popoverElement.classList.remove('show');
                this.updateCalendar();
            });
        });
    }
    
    updateCalendar() {
        this.titleText.textContent = `${this.months[this.currentMonth]}, ${this.currentYear}`;
        
        const days = this.generateDays();
        this.daysGrid.innerHTML = days.map(d => {
            const dateStr = formatDateLocal(d.date);
            const isSelected = this.selectedDates.has(dateStr);
            const hasData = this.availableDates.has(dateStr);
            const classes = ['calendar-day'];
            if (!d.isCurrentMonth) classes.push('other-month');
            if (isSelected) classes.push('selected');
            if (hasData) classes.push('has-data');
            
            return `
                <button class="${classes.join(' ')}" type="button" data-date="${dateStr}">
                    ${d.dayNum}
                </button>
            `;
        }).join('');
        
        this.daysGrid.querySelectorAll('.calendar-day').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const dateStr = btn.dataset.date;
                const clickedDate = new Date(dateStr + 'T00:00:00');
                
                if (clickedDate.getMonth() !== this.currentMonth || clickedDate.getFullYear() !== this.currentYear) {
                    this.currentMonth = clickedDate.getMonth();
                    this.currentYear = clickedDate.getFullYear();
                }
                
                if (this.multiSelect) {
                    if (this.selectedDates.has(dateStr)) {
                        this.selectedDates.delete(dateStr);
                    } else {
                        this.selectedDates.add(dateStr);
                    }
                    this.updateCalendar();
                    this.onSelect(this.selectedDates);
                } else {
                    this.selectedDates.clear();
                    this.selectedDates.add(dateStr);
                    this.updateCalendar();
                    this.onSelect(this.selectedDates);
                    
                    const dropdownEl = this.container.closest('.dropdown');
                    if (dropdownEl) {
                        const toggleBtn = dropdownEl.querySelector('.dropdown-toggle');
                        if (toggleBtn) {
                            const dropdown = bootstrap.Dropdown.getInstance(toggleBtn) || new bootstrap.Dropdown(toggleBtn);
                            dropdown.hide();
                        }
                    }
                }
            });
        });
    }
    
    generateDays() {
        const firstDayOfMonth = new Date(this.currentYear, this.currentMonth, 1);
        const lastDayOfMonth = new Date(this.currentYear, this.currentMonth + 1, 0);
        const daysInMonth = lastDayOfMonth.getDate();
        
        const startDayOfWeek = firstDayOfMonth.getDay();
        const days = [];
        
        const prevMonthLastDay = new Date(this.currentYear, this.currentMonth, 0).getDate();
        for (let i = startDayOfWeek - 1; i >= 0; i--) {
            const d = prevMonthLastDay - i;
            const prevMonthDate = new Date(this.currentYear, this.currentMonth - 1, d);
            days.push({
                date: prevMonthDate,
                dayNum: d,
                isCurrentMonth: false
            });
        }
        
        for (let d = 1; d <= daysInMonth; d++) {
            const currentDate = new Date(this.currentYear, this.currentMonth, d);
            days.push({
                date: currentDate,
                dayNum: d,
                isCurrentMonth: true
            });
        }
        
        const totalCells = 42;
        const remainingCells = totalCells - days.length;
        for (let d = 1; d <= remainingCells; d++) {
            const nextMonthDate = new Date(this.currentYear, this.currentMonth + 1, d);
            days.push({
                date: nextMonthDate,
                dayNum: d,
                isCurrentMonth: false
            });
        }
        
        return days;
    }
}
