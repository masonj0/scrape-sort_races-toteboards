class CheckmateApp {
    constructor() {
        this.currentTab = 'qualified';
        this.refreshInterval = null;
        this.isRefreshing = false;

        this.init();
        this.startAutoRefresh();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
    }

    bindEvents() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshData(true); // Force refresh
        });

        document.getElementById('settings-btn').addEventListener('click', () => {
            this.openSettingsModal();
        });

        document.querySelector('.close').addEventListener('click', () => {
            this.closeSettingsModal();
        });

        document.getElementById('save-settings').addEventListener('click', () => {
            this.saveSettings();
        });

        this.refreshInterval = setInterval(() => {
            this.refreshData(false);
        }, 300000);
    }

    async loadInitialData() {
        await this.updateSystemStatus();
        await this.loadRaceData();
        await this.loadAdapterStatus();
    }

    async refreshData(isManual = false) {
        if (this.isRefreshing) return;

        this.isRefreshing = true;
        const refreshBtn = document.getElementById('refresh-btn');
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';

        try {
            if (isManual) {
                await fetch('/api/refresh', { method: 'POST' });
                await new Promise(resolve => setTimeout(resolve, 2000));
                await this.waitForRefreshComplete();
            }

            await this.loadInitialData();

        } catch (error) {
            console.error('Refresh failed:', error);
            this.showNotification('Refresh failed. Please try again.', 'error');
        } finally {
            this.isRefreshing = false;
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh Data';
        }
    }

    async waitForRefreshComplete() {
        let attempts = 0;
        const maxAttempts = 30; // 30 seconds timeout

        while (attempts < maxAttempts) {
            const status = await fetch('/api/status').then(r => r.json());
            if (!status.is_fetching) break;

            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
        }
    }

    async updateSystemStatus() {
        try {
            const status = await fetch('/api/status').then(r => r.json());
            document.getElementById('system-status').textContent = 'Online';
            document.getElementById('last-update').textContent =
                status.last_update ? new Date(status.last_update).toLocaleTimeString() : 'Never';
            document.getElementById('races-count').textContent =
                `${status.races_count} races`;
            document.getElementById('qualified-count').textContent =
                `${status.qualified_count} qualified`;

        } catch (error) {
            console.error('Status update failed:', error);
            document.getElementById('system-status').textContent = 'Error';
        }
    }

    async loadRaceData() {
        try {
            const [qualifiedData, allData] = await Promise.all([
                fetch('/api/races/qualified').then(r => r.json()),
                fetch('/api/races/all').then(r => r.json())
            ]);

            this.renderQualifiedRaces(qualifiedData.qualified_races);
            this.renderAllRaces(allData.races);

        } catch (error) {
            console.error('Race data loading failed:', error);
            this.showNotification('Failed to load race data', 'error');
        }
    }

    renderQualifiedRaces(qualifiedRaces) {
        const container = document.getElementById('qualified-races');

        if (qualifiedRaces.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h3>No Qualified Races Found</h3>
                    <p>No races currently meet the Checkmate criteria. Check back soon!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = qualifiedRaces.map(race => `
            <div class="race-card qualified">
                <div class="race-header">
                    <div class="track-info">
                        <h3>${race.track_name}</h3>
                        <span class="race-number">Race ${race.race_number || 'TBD'}</span>
                        <span class="post-time">${this.formatPostTime(race.post_time)}</span>
                    </div>
                    <div class="checkmate-score">
                        <div class="score-badge qualified">
                            <i class="fas fa-star"></i>
                            ${race.checkmate_score}
                        </div>
                    </div>
                </div>

                <div class="analysis-factors">
                    ${this.renderTrifectaFactors(race.trifecta_factors)}
                </div>

                <div class="runners-preview">
                    <h4><i class="fas fa-horse"></i> Runners (${race.runners.length})</h4>
                    <div class="runners-grid">
                        ${race.runners.slice(0, 6).map(runner => `
                            <div class="runner-chip">
                                <span class="runner-number">${runner.number || '?'}</span>
                                <span class="runner-name">${runner.name}</span>
                                <span class="runner-odds">${this.formatOdds(runner.odds)}</span>
                            </div>
                        `).join('')}
                        ${race.runners.length > 6 ? `<div class="runner-chip more">+${race.runners.length - 6} more</div>` : ''}
                    </div>
                </div>

                <div class="race-footer">
                    <span class="source-badge">
                        <i class="fas fa-database"></i>
                        ${race.source || 'Unknown'}
                    </span>
                    <button class="btn btn-sm btn-outline" onclick="app.showRaceDetails('${race.race_id}')">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderTrifectaFactors(factors) {
        if (!factors) return '';

        return Object.entries(factors).map(([key, factor]) => {
            const icon = factor.ok ? 'fa-check-circle' : 'fa-times-circle';
            const status = factor.ok ? 'positive' : 'negative';

            return `
                <div class="factor ${status}">
                    <i class="fas ${icon}"></i>
                    <span class="factor-name">${this.humanizeFactorName(key)}</span>
                    <span class="factor-points">${factor.points > 0 ? '+' : ''}${factor.points}</span>
                    <div class="factor-tooltip">${factor.reason}</div>
                </div>
            `;
        }).join('');
    }

    renderAllRaces(allRaces) {
        const container = document.getElementById('all-races');

        if (allRaces.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-horse"></i>
                    <h3>No Race Data Available</h3>
                    <p>Unable to fetch race data from any sources. Please check data source status.</p>
                </div>
            `;
            return;
        }

        const sortedRaces = allRaces.sort((a, b) => {
            if (a.qualified && !b.qualified) return -1;
            if (!a.qualified && b.qualified) return 1;
            return b.checkmate_score - a.checkmate_score;
        });

        container.innerHTML = sortedRaces.map(race => `
            <div class="race-card ${race.qualified ? 'qualified' : 'not-qualified'}">
                <div class="race-header">
                    <div class="track-info">
                        <h3>${race.track_name}</h3>
                        <span class="race-number">Race ${race.race_number || 'TBD'}</span>
                        <span class="post-time">${this.formatPostTime(race.post_time)}</span>
                    </div>
                    <div class="checkmate-score">
                        <div class="score-badge ${race.qualified ? 'qualified' : 'not-qualified'}">
                            ${race.qualified ? '<i class="fas fa-star"></i>' : '<i class="fas fa-minus-circle"></i>'}
                            ${race.checkmate_score}
                        </div>
                    </div>
                </div>

                <div class="runners-summary">
                    <span>${race.runners.length} runners</span>
                    <span>Source: ${race.source || 'Unknown'}</span>
                </div>
            </div>
        `).join('');
    }

    async loadAdapterStatus() {
        try {
            const data = await fetch('/api/adapters/status').then(r => r.json());
            this.renderAdapterStatus(data.adapters);
        } catch (error) {
            console.error('Adapter status loading failed:', error);
        }
    }

    renderAdapterStatus(adapters) {
        const container = document.getElementById('adapter-status');

        container.innerHTML = adapters.map(adapter => `
            <div class="adapter-card ${adapter.status.toLowerCase()}">
                <div class="adapter-header">
                    <h3>${adapter.adapter_id}</h3>
                    <div class="status-indicator ${adapter.status.toLowerCase()}">
                        <i class="fas ${adapter.status === 'OK' ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i>
                        ${adapter.status}
                    </div>
                </div>
                <div class="adapter-stats">
                    <div class="stat">
                        <i class="fas fa-horse"></i>
                        <span>${adapter.races_found} races found</span>
                    </div>
                </div>
                <div class="adapter-notes">
                    ${adapter.notes || 'No additional notes'}
                </div>
                ${adapter.error_message ? `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        ${adapter.error_message}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
        this.currentTab = tabName;
    }

    formatPostTime(postTime) {
        if (!postTime) return 'TBD';
        const date = new Date(postTime);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    formatOdds(odds) {
        if (!odds) return 'N/A';
        return odds.toFixed(1);
    }

    humanizeFactorName(key) {
        const names = {
            'fieldSize': 'Field Size',
            'favoriteOdds': 'Favorite Odds',
            'secondFavoriteOdds': '2nd Favorite'
        };
        return names[key] || key;
    }

    async openSettingsModal() {
        const settings = await fetch('/api/settings').then(r => r.json());
        document.getElementById('qualification-score').value = settings.QUALIFICATION_SCORE;
        document.getElementById('field-size-min').value = settings.FIELD_SIZE_OPTIMAL_MIN;
        document.getElementById('field-size-max').value = settings.FIELD_SIZE_OPTIMAL_MAX;
        document.getElementById('max-fav-odds').value = settings.MAX_FAV_ODDS;
        document.getElementById('settings-modal').style.display = 'block';
    }

    closeSettingsModal() {
        document.getElementById('settings-modal').style.display = 'none';
    }

    async saveSettings() {
        const newSettings = {
            QUALIFICATION_SCORE: parseFloat(document.getElementById('qualification-score').value),
            FIELD_SIZE_OPTIMAL_MIN: parseInt(document.getElementById('field-size-min').value),
            FIELD_SIZE_OPTIMAL_MAX: parseInt(document.getElementById('field-size-max').value),
            MAX_FAV_ODDS: parseFloat(document.getElementById('max-fav-odds').value)
        };

        try {
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newSettings)
            });
            this.closeSettingsModal();
            this.showNotification('Settings saved successfully!', 'success');
            await this.refreshData(true);
        } catch (error) {
            console.error('Settings save failed:', error);
            this.showNotification('Failed to save settings', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check' : 'fa-times'}"></i> ${message}`;
        document.body.appendChild(notification);
        setTimeout(() => { notification.remove(); }, 3000);
    }

    startAutoRefresh() {
        setInterval(() => {
            this.updateSystemStatus();
        }, 30000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new CheckmateApp();
});