class CheckmateApp {
    constructor() {
        this.currentTab = 'qualified';
        this.isRefreshing = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
    }

    bindEvents() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.currentTarget.dataset.tab));
        });
        document.getElementById('refresh-btn').addEventListener('click', () => this.refreshData(true));
        // Modal events are for Phase 4
    }

    async loadInitialData() {
        this.setLoading(true);
        await Promise.all([
            this.updateSystemStatus(),
            this.loadRaceData(),
            this.loadAdapterStatus()
        ]);
        this.setLoading(false);
    }

    async refreshData(isManual = false) {
        // Full implementation in Phase 4
        if (isManual) this.loadInitialData();
    }

    setLoading(isLoading) {
        const refreshBtn = document.getElementById('refresh-btn');
        if (isLoading) {
            this.isRefreshing = true;
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        } else {
            this.isRefreshing = false;
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh Data';
        }
    }

    async updateSystemStatus() {
        try {
            const status = await fetch('/api/status').then(r => r.json());
            document.getElementById('system-status').textContent = 'Online';
            document.getElementById('last-update').textContent = status.last_update ? new Date(status.last_update).toLocaleTimeString() : 'Never';
            document.getElementById('races-count').textContent = `${status.races_count} races`;
            document.getElementById('qualified-count').textContent = `${status.qualified_count} qualified`;
        } catch (error) {
            document.getElementById('system-status').textContent = 'Offline';
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
        }
    }

    renderQualifiedRaces(races) {
        const container = document.getElementById('qualified-races');
        if (!races || races.length === 0) {
            container.innerHTML = `<div class="empty-state"><i class="fas fa-search"></i><h3>No Qualified Races Found</h3><p>No races currently meet the Checkmate criteria.</p></div>`;
            return;
        }
        container.innerHTML = races.map(race => this.createRaceCard(race)).join('');
    }

    renderAllRaces(races) {
        const container = document.getElementById('all-races');
        if (!races || races.length === 0) {
            container.innerHTML = `<div class="empty-state"><i class="fas fa-horse"></i><h3>No Race Data Available</h3><p>Could not fetch race data from any source.</p></div>`;
            return;
        }
        const sorted = races.sort((a, b) => (b.qualified - a.qualified) || (b.checkmate_score - a.checkmate_score));
        container.innerHTML = sorted.map(race => this.createRaceCard(race)).join('');
    }

    createRaceCard(race) {
        const isQualified = race.qualified;
        return `
            <div class="race-card ${isQualified ? 'qualified' : 'not-qualified'}">
                <div class="race-header">
                    <div class="track-info">
                        <h3>${race.track_name}</h3>
                        <span class="race-number">Race ${race.race_number || 'TBD'}</span>
                        <span class="post-time">${this.formatPostTime(race.post_time)}</span>
                    </div>
                    <div class="checkmate-score">
                        <div class="score-badge ${isQualified ? 'qualified' : 'not-qualified'}">
                            <i class="fas ${isQualified ? 'fa-star' : 'fa-minus-circle'}"></i>
                            ${race.checkmate_score}
                        </div>
                    </div>
                </div>
                ${isQualified ? this.renderTrifectaFactors(race.trifecta_factors) : this.renderRunnersSummary(race)}
                <div class="race-footer">
                    <span class="source-badge"><i class="fas fa-database"></i> ${race.source || 'Unknown'}</span>
                </div>
            </div>
        `;
    }

    renderRunnersSummary(race) {
        return `<div class="runners-summary"><span>${race.runners.length} runners</span></div>`;
    }

    renderTrifectaFactors(factors) {
        if (!factors) return '';
        const factorsHtml = Object.entries(factors).map(([key, factor]) => {
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
        return `<div class="analysis-factors">${factorsHtml}</div>`;
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
        if (!adapters || adapters.length === 0) {
             container.innerHTML = `<div class="empty-state"><i class="fas fa-plug"></i><h3>No Adapters Reported</h3><p>The engine did not report any adapter status.</p></div>`;
             return;
        }
        container.innerHTML = adapters.map(adapter => {
            const isOk = adapter.status === 'OK';
            return `
            <div class="adapter-card ${isOk ? 'ok' : 'error'}">
                <div class="adapter-header">
                    <h3>${adapter.adapter_id}</h3>
                    <div class="status-indicator ${isOk ? 'ok' : 'error'}">
                        <i class="fas ${isOk ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i> ${adapter.status}
                    </div>
                </div>
                <div class="adapter-notes">${adapter.notes || (isOk ? 'No notes.' : adapter.error_message)}</div>
            </div>
        `}).join('');
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
        return new Date(postTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    humanizeFactorName(key) {
        const names = { 'fieldSize': 'Field Size', 'favoriteOdds': 'Favorite Odds', 'secondFavoriteOdds': '2nd Favorite' };
        return names[key] || key;
    }
}

document.addEventListener('DOMContentLoaded', () => { window.app = new CheckmateApp(); });