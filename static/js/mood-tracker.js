/**
 * moodtracker.js
 * Zenalyze - Mood Tracking JavaScript
 * Handles mood logging, charts, patterns, and insights
 */

class MoodTracker {
    constructor() {
        this.moodOptions = document.querySelectorAll('.mood-option');
        this.moodForm = document.getElementById('mood-form');
        this.moodDate = document.getElementById('mood-date');
        this.moodNote = document.getElementById('mood-note');
        this.moodIntensity = document.getElementById('mood-intensity');
        this.moodTriggers = document.querySelectorAll('.trigger-checkbox');
        this.saveButton = document.getElementById('save-mood');
        this.chartCanvas = document.getElementById('mood-chart');
        this.insightsContainer = document.getElementById('mood-insights');
        this.calendarContainer = document.getElementById('mood-calendar');
        
        this.currentMood = null;
        this.moodData = [];
        this.chart = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadMoodData();
        this.initMoodChart();
        this.initCalendar();
        this.initIntensitySlider();
        this.checkDailyReminder();
    }
    
    bindEvents() {
        // Mood selection
        this.moodOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectMood(option);
            });
        });
        
        // Save mood
        if (this.saveButton) {
            this.saveButton.addEventListener('click', () => {
                this.saveMoodEntry();
            });
        }
        
        // Date picker
        if (this.moodDate) {
            this.moodDate.valueAsDate = new Date();
            this.moodDate.addEventListener('change', () => {
                this.loadMoodForDate(this.moodDate.value);
            });
        }
        
        // Intensity slider
        if (this.moodIntensity) {
            this.moodIntensity.addEventListener('input', (e) => {
                this.updateIntensityLabel(e.target.value);
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 's') {
                    e.preventDefault();
                    this.saveMoodEntry();
                }
            }
        });
    }
    
    selectMood(option) {
        // Remove selected class from all options
        this.moodOptions.forEach(opt => {
            opt.classList.remove('selected', 'active');
        });
        
        // Add selected class to clicked option
        option.classList.add('selected', 'active');
        
        // Store current mood
        this.currentMood = {
            emoji: option.querySelector('.mood-option-emoji').textContent,
            label: option.querySelector('.mood-option-label').textContent,
            value: option.dataset.moodValue || option.querySelector('.mood-option-label').textContent.toLowerCase()
        };
        
        // Animate selection
        option.style.transform = 'scale(1.1)';
        setTimeout(() => {
            option.style.transform = '';
        }, 200);
    }
    
    async saveMoodEntry() {
        if (!this.currentMood) {
            alert('Please select a mood first');
            return;
        }
        
        const moodData = {
            mood: this.currentMood.value,
            emoji: this.currentMood.emoji,
            label: this.currentMood.label,
            intensity: this.moodIntensity ? this.moodIntensity.value : 5,
            note: this.moodNote ? this.moodNote.value : '',
            triggers: this.getSelectedTriggers(),
            date: this.moodDate ? this.moodDate.value : new Date().toISOString().split('T')[0],
            timestamp: new Date().toISOString()
        };
        
        try {
            // Show loading state
            this.saveButton.disabled = true;
            this.saveButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';
            
            // Save to localStorage
            this.saveToLocalStorage(moodData);
            
            // Send to server (if logged in)
            if (window.userLoggedIn) {
                await this.saveToServer(moodData);
            }
            
            // Show success message
            this.showNotification('Mood saved successfully!', 'success');
            
            // Reset form
            this.resetForm();
            
            // Update chart and insights
            this.loadMoodData();
            this.updateMoodChart();
            this.updateInsights();
            this.updateCalendar();
            
        } catch (error) {
            console.error('Error saving mood:', error);
            this.showNotification('Error saving mood. Please try again.', 'error');
        } finally {
            // Reset button
            this.saveButton.disabled = false;
            this.saveButton.innerHTML = '<i class="bi bi-check-circle"></i> Save Mood';
        }
    }
    
    saveToLocalStorage(moodData) {
        let entries = JSON.parse(localStorage.getItem('moodEntries') || '[]');
        entries.push(moodData);
        
        // Keep only last 30 days
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        
        entries = entries.filter(entry => {
            const entryDate = new Date(entry.date);
            return entryDate >= thirtyDaysAgo;
        });
        
        localStorage.setItem('moodEntries', JSON.stringify(entries));
    }
    
    async saveToServer(moodData) {
        const response = await fetch('/api/save-mood.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(moodData)
        });
        
        if (!response.ok) {
            throw new Error('Server error');
        }
        
        return await response.json();
    }
    
    loadMoodData() {
        this.moodData = JSON.parse(localStorage.getItem('moodEntries') || '[]');
        
        // Sort by date
        this.moodData.sort((a, b) => new Date(a.date) - new Date(b.date));
    }
    
    initMoodChart() {
        if (!this.chartCanvas) return;
        
        const ctx = this.chartCanvas.getContext('2d');
        
        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Prepare data
        const dates = this.moodData.map(entry => {
            const d = new Date(entry.date);
            return `${d.getMonth() + 1}/${d.getDate()}`;
        });
        
        const intensities = this.moodData.map(entry => entry.intensity);
        
        // Create new chart
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Mood Intensity',
                    data: intensities,
                    borderColor: '#5D8AA8',
                    backgroundColor: 'rgba(93, 138, 168, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: intensities.map(i => this.getMoodColor(i)),
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const entry = this.moodData[context.dataIndex];
                                return [
                                    `Intensity: ${entry.intensity}/10`,
                                    `Mood: ${entry.label}`,
                                    entry.note ? `Note: ${entry.note}` : null
                                ].filter(Boolean);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        grid: {
                            color: 'rgba(93, 138, 168, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    updateMoodChart() {
        if (this.chart) {
            const dates = this.moodData.map(entry => {
                const d = new Date(entry.date);
                return `${d.getMonth() + 1}/${d.getDate()}`;
            });
            
            const intensities = this.moodData.map(entry => entry.intensity);
            
            this.chart.data.labels = dates;
            this.chart.data.datasets[0].data = intensities;
            this.chart.data.datasets[0].pointBackgroundColor = intensities.map(i => this.getMoodColor(i));
            
            this.chart.update();
        }
    }
    
    getMoodColor(intensity) {
        const colors = [
            '#dc3545', // Low - Red
            '#fd7e14', // Orange
            '#ffc107', // Yellow
            '#28a745', // Light Green
            '#20c997', // Green
            '#17a2b8', // Teal
            '#5D8AA8'  // Blue - High
        ];
        const index = Math.floor(intensity / 2);
        return colors[Math.min(index, colors.length - 1)];
    }
    
    initIntensitySlider() {
        if (this.moodIntensity) {
            this.updateIntensityLabel(this.moodIntensity.value);
        }
    }
    
    updateIntensityLabel(value) {
        const label = document.getElementById('intensity-value');
        if (label) {
            label.textContent = value;
            
            // Update color
            const color = this.getMoodColor(value);
            label.style.color = color;
        }
    }
    
    getSelectedTriggers() {
        const triggers = [];
        this.moodTriggers.forEach(checkbox => {
            if (checkbox.checked) {
                triggers.push(checkbox.value);
            }
        });
        return triggers;
    }
    
    loadMoodForDate(date) {
        const entry = this.moodData.find(e => e.date === date);
        
        if (entry) {
            // Select mood
            const moodOption = Array.from(this.moodOptions).find(
                opt => opt.querySelector('.mood-option-label').textContent.toLowerCase() === entry.mood
            );
            
            if (moodOption) {
                this.selectMood(moodOption);
            }
            
            // Set intensity
            if (this.moodIntensity) {
                this.moodIntensity.value = entry.intensity;
                this.updateIntensityLabel(entry.intensity);
            }
            
            // Set note
            if (this.moodNote) {
                this.moodNote.value = entry.note || '';
            }
            
            // Set triggers
            this.moodTriggers.forEach(checkbox => {
                checkbox.checked = entry.triggers?.includes(checkbox.value) || false;
            });
            
            this.showNotification('Loaded mood entry from this date', 'info');
        } else {
            this.resetForm();
        }
    }
    
    resetForm() {
        // Remove mood selection
        this.moodOptions.forEach(opt => {
            opt.classList.remove('selected', 'active');
        });
        
        // Reset intensity
        if (this.moodIntensity) {
            this.moodIntensity.value = 5;
            this.updateIntensityLabel(5);
        }
        
        // Clear note
        if (this.moodNote) {
            this.moodNote.value = '';
        }
        
        // Uncheck triggers
        this.moodTriggers.forEach(checkbox => {
            checkbox.checked = false;
        });
        
        this.currentMood = null;
    }
    
    updateInsights() {
        if (!this.insightsContainer) return;
        
        if (this.moodData.length < 3) {
            this.insightsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    Track at least 3 moods to see insights about your emotional patterns.
                </div>
            `;
            return;
        }
        
        const insights = this.generateInsights();
        
        let html = '<div class="insights-grid">';
        
        insights.forEach(insight => {
            html += `
                <div class="insight-card">
                    <div class="insight-icon">
                        <i class="bi ${insight.icon}"></i>
                    </div>
                    <div class="insight-content">
                        <h6>${insight.title}</h6>
                        <p>${insight.text}</p>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        this.insightsContainer.innerHTML = html;
    }
    
    generateInsights() {
        const insights = [];
        
        // Average mood
        const avgIntensity = this.moodData.reduce((sum, e) => sum + e.intensity, 0) / this.moodData.length;
        insights.push({
            icon: 'bi-bar-chart',
            title: 'Average Mood',
            text: `Your average mood intensity is ${avgIntensity.toFixed(1)}/10`
        });
        
        // Most common mood
        const moodCounts = {};
        this.moodData.forEach(e => {
            moodCounts[e.mood] = (moodCounts[e.mood] || 0) + 1;
        });
        
        const mostCommon = Object.entries(moodCounts).sort((a, b) => b[1] - a[1])[0];
        if (mostCommon) {
            insights.push({
                icon: 'bi-emoji-smile',
                title: 'Most Common Mood',
                text: `You feel "${mostCommon[0]}" most often (${mostCommon[1]} times)`
            });
        }
        
        // Trend
        if (this.moodData.length >= 5) {
            const first = this.moodData[0].intensity;
            const last = this.moodData[this.moodData.length - 1].intensity;
            const trend = last - first;
            
            insights.push({
                icon: trend > 0 ? 'bi-graph-up-arrow' : 'bi-graph-down-arrow',
                title: 'Mood Trend',
                text: trend > 0 ? 
                    'Your mood is generally improving' : 
                    'Your mood has been decreasing. Consider reaching out for support.'
            });
        }
        
        // Best time of day
        const timeMoods = {};
        this.moodData.forEach(e => {
            const hour = new Date(e.timestamp).getHours();
            const timeOfDay = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
            
            if (!timeMoods[timeOfDay]) {
                timeMoods[timeOfDay] = { total: 0, count: 0 };
            }
            timeMoods[timeOfDay].total += e.intensity;
            timeMoods[timeOfDay].count++;
        });
        
        let bestTime = null;
        let bestAvg = 0;
        
        Object.entries(timeMoods).forEach(([time, data]) => {
            const avg = data.total / data.count;
            if (avg > bestAvg) {
                bestAvg = avg;
                bestTime = time;
            }
        });
        
        if (bestTime) {
            insights.push({
                icon: 'bi-sun',
                title: 'Best Time of Day',
                text: `You tend to feel best in the ${bestTime}`
            });
        }
        
        return insights;
    }
    
    initCalendar() {
        if (!this.calendarContainer) return;
        
        this.renderCalendar();
    }
    
    renderCalendar() {
        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth();
        
        const firstDay = new Date(year, month, 1).getDay();
        const lastDate = new Date(year, month + 1, 0).getDate();
        
        let html = `
            <div class="calendar-header">
                <button class="calendar-prev"><i class="bi bi-chevron-left"></i></button>
                <h6>${today.toLocaleString('default', { month: 'long' })} ${year}</h6>
                <button class="calendar-next"><i class="bi bi-chevron-right"></i></button>
            </div>
            <div class="calendar-weekdays">
                <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span>
                <span>Thu</span><span>Fri</span><span>Sat</span>
            </div>
            <div class="calendar-grid">
        `;
        
        // Empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="calendar-day empty"></div>';
        }
        
        // Fill in the days
        for (let date = 1; date <= lastDate; date++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
            const moodEntry = this.moodData.find(e => e.date === dateStr);
            
            let classes = 'calendar-day';
            if (moodEntry) {
                classes += ' has-mood';
                if (moodEntry.intensity >= 7) classes += ' high';
                else if (moodEntry.intensity >= 4) classes += ' medium';
                else classes += ' low';
            }
            
            html += `
                <div class="${classes}" data-date="${dateStr}">
                    ${date}
                    ${moodEntry ? `<span class="mood-indicator">${moodEntry.emoji}</span>` : ''}
                </div>
            `;
        }
        
        html += '</div>';
        
        this.calendarContainer.innerHTML = html;
        
        // Add click handlers
        this.calendarContainer.querySelectorAll('.calendar-day:not(.empty)').forEach(day => {
            day.addEventListener('click', () => {
                const date = day.dataset.date;
                if (date) {
                    this.moodDate.value = date;
                    this.loadMoodForDate(date);
                }
            });
        });
    }
    
    checkDailyReminder() {
        const lastReminder = localStorage.getItem('lastMoodReminder');
        const today = new Date().toDateString();
        
        if (lastReminder !== today) {
            // Check if user has logged mood today
            const todayStr = new Date().toISOString().split('T')[0];
            const hasLogged = this.moodData.some(e => e.date === todayStr);
            
            if (!hasLogged) {
                setTimeout(() => {
                    if (confirm('Would you like to log your mood for today?')) {
                        document.querySelector('.mood-card')?.scrollIntoView({ behavior: 'smooth' });
                    }
                }, 5000);
            }
            
            localStorage.setItem('lastMoodReminder', today);
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    exportData() {
        const dataStr = JSON.stringify(this.moodData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `mood-data-${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }
    
    importData(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            try {
                const importedData = JSON.parse(e.target.result);
                
                if (Array.isArray(importedData)) {
                    this.moodData = importedData;
                    localStorage.setItem('moodEntries', JSON.stringify(this.moodData));
                    
                    this.updateMoodChart();
                    this.updateInsights();
                    this.updateCalendar();
                    
                    this.showNotification('Data imported successfully!', 'success');
                } else {
                    throw new Error('Invalid data format');
                }
            } catch (error) {
                this.showNotification('Error importing data', 'error');
            }
        };
        
        reader.readAsText(file);
    }
}

// Initialize mood tracker when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.mood-tracker-container')) {
        window.moodTracker = new MoodTracker();
    }
});

// Make utility functions available globally
window.exportMoodData = () => {
    if (window.moodTracker) {
        window.moodTracker.exportData();
    }
};

window.importMoodData = (file) => {
    if (window.moodTracker) {
        window.moodTracker.importData(file);
    }
};