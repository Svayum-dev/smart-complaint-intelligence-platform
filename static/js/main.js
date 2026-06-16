/* ─────────────────────────────────────────────
   SMART COMPLAINT INTELLIGENCE PLATFORM
   Main JavaScript — Interactions & Charts
───────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initClock();
  initCounters();
  initAlertClose();
  autoHideFlash();
  initStatusUpdates();
  initTableSort();
  // Note: Analytics charts are initialized from analytics.html inline script
  // to avoid double-init conflicts with Chart.js canvas reuse.
});

window.addEventListener('load', () => {
  const loader = document.getElementById('pageLoader');
  if (loader) {
    loader.classList.add('hidden');
    setTimeout(() => loader.remove(), 400);
  }
});

/* ══════════════════════════════════════════
   SIDEBAR TOGGLE
══════════════════════════════════════════ */
function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const toggleBtn = document.getElementById('sidebarToggle');
  const overlay = document.getElementById('sidebarOverlay');

  if (!sidebar || !toggleBtn) return;

  const isMobile = () => window.innerWidth <= 768;

  function closeMobile() {
    sidebar.classList.remove('mobile-open');
    overlay && overlay.classList.remove('active');
  }

  toggleBtn.addEventListener('click', () => {
    if (isMobile()) {
      sidebar.classList.toggle('mobile-open');
      overlay && overlay.classList.toggle('active');
    } else {
      sidebar.classList.toggle('collapsed');
      mainContent && mainContent.classList.toggle('expanded');
      // Save state
      const isCollapsed = sidebar.classList.contains('collapsed');
      localStorage.setItem('sidebarCollapsed', isCollapsed);
    }
  });

  overlay && overlay.addEventListener('click', closeMobile);

  // Restore collapsed state on desktop
  if (!isMobile()) {
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true') {
      sidebar.classList.add('collapsed');
      mainContent && mainContent.classList.add('expanded');
    }
  }

  // Handle resize
  window.addEventListener('resize', () => {
    if (!isMobile()) {
      closeMobile();
    }
  });
}

/* ══════════════════════════════════════════
   LIVE CLOCK
══════════════════════════════════════════ */
function initClock() {
  const el = document.getElementById('liveClock');
  if (!el) return;

  function tick() {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
  tick();
  setInterval(tick, 1000);
}

/* ══════════════════════════════════════════
   ANIMATED COUNTER
══════════════════════════════════════════ */
function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  counters.forEach(el => observer.observe(el));
}

function animateCounter(el) {
  const target = parseInt(el.getAttribute('data-count'), 10);
  const duration = 1200;
  const start = performance.now();

  function update(time) {
    const elapsed = time - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
    el.textContent = Math.round(eased * target).toLocaleString();
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

/* ══════════════════════════════════════════
   ALERT CLOSE
══════════════════════════════════════════ */
function initAlertClose() {
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.transition = 'opacity 0.3s, transform 0.3s';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-8px)';
        setTimeout(() => alert.remove(), 320);
      }
    });
  });
}

function autoHideFlash() {
  const flashes = document.querySelectorAll('.alert');
  flashes.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.6s, transform 0.6s';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 650);
    }, 5000);
  });
}

/* ══════════════════════════════════════════
   STATUS UPDATES (AJAX)
══════════════════════════════════════════ */
function initStatusUpdates() {
  document.querySelectorAll('.status-select').forEach(select => {
    select.addEventListener('change', async function () {
      const id = this.dataset.id;
      const newStatus = this.value;
      const badge = this.closest('tr')?.querySelector('.status-badge');

      select.disabled = true;
      if (badge) badge.style.opacity = '0.4';

      try {
        const res = await fetch('/api/update-status', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: parseInt(id), status: newStatus })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Status updated to "${newStatus}"`, 'success');
          if (badge) updateStatusBadge(badge, newStatus);
        }
      } catch (err) {
        showToast('Failed to update status.', 'error');
      } finally {
        select.disabled = false;
        if (badge) badge.style.opacity = '1';
      }
    });
  });
}

function updateStatusBadge(badge, status) {
  badge.className = 'badge status-badge';
  const map = {
    'Open': 'badge-open',
    'In Progress': 'badge-progress',
    'Resolved': 'badge-resolved',
  };
  const cls = map[status] || 'badge-open';
  badge.classList.add(cls);
  badge.innerHTML = `<span class="badge-dot"></span>${status}`;
}

/* ══════════════════════════════════════════
   TOAST NOTIFICATIONS
══════════════════════════════════════════ */
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${icons[type] || '✅'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s, transform 0.4s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 420);
  }, 3500);
}

/* ══════════════════════════════════════════
   TABLE SORT (visual only — server re-sorts)
══════════════════════════════════════════ */
function initTableSort() {
  document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const sort = th.dataset.sort;
      const url = new URL(window.location.href);
      const currentSort = url.searchParams.get('sort');
      const currentOrder = url.searchParams.get('order') || 'desc';
      url.searchParams.set('sort', sort);
      url.searchParams.set('order', currentSort === sort && currentOrder === 'desc' ? 'asc' : 'desc');
      url.searchParams.set('page', 1);
      window.location.href = url.toString();
    });
  });

  // Highlight sorted column
  const url = new URL(window.location.href);
  const currentSort = url.searchParams.get('sort');
  if (currentSort) {
    const sorted = document.querySelector(`th[data-sort="${currentSort}"]`);
    if (sorted) {
      sorted.classList.add('sorted');
      const order = url.searchParams.get('order') || 'desc';
      sorted.innerHTML += ` <span style="opacity:0.7">${order === 'asc' ? '↑' : '↓'}</span>`;
    }
  }
}

/* ══════════════════════════════════════════
   ANALYTICS CHARTS (Chart.js)
══════════════════════════════════════════ */
const CHART_COLORS = {
  accent: '#6c63ff',
  success: '#00d4aa',
  warning: '#ffb347',
  danger: '#ff6b6b',
  critical: '#ff4757',
  info: '#4fc3f7',
  muted: '#8892b0',
  purple: '#a78bfa',
  pink: '#f472b6',
  cyan: '#22d3ee',
  emerald: '#34d399',
  orange: '#fb923c',
};

const CATEGORY_COLORS = [
  '#6c63ff', '#00d4aa', '#ffb347', '#ff6b6b',
  '#4fc3f7', '#a78bfa', '#f472b6', '#22d3ee'
];

const PRIORITY_COLORS = {
  'Low': '#8892b0',
  'Medium': '#ffb347',
  'High': '#ff6b6b',
  'Critical': '#ff4757',
};

const STATUS_COLORS = {
  'Open': '#ffb347',
  'In Progress': '#4fc3f7',
  'Resolved': '#00d4aa',
};

Chart.defaults.color = '#8892b0';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(17, 24, 39, 0.95)';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 10;
Chart.defaults.plugins.legend.display = false;

async function loadAnalyticsCharts() {
  try {
    const res = await fetch('/api/analytics');
    const data = await res.json();
    buildCategoryChart(data.by_category);
    buildStatusChart(data.by_status);
    buildPriorityChart(data.by_priority);
    buildTrendChart(data.monthly_trend);
  } catch (err) {
    console.error('Failed to load analytics:', err);
  }
}

function buildCategoryChart(data) {
  const ctx = document.getElementById('categoryChart');
  if (!ctx || !data.length) return;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.category.replace(' & ', '\n& ')),
      datasets: [{
        data: data.map(d => d.count),
        backgroundColor: CATEGORY_COLORS.map(c => c + '99'),
        borderColor: CATEGORY_COLORS,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: {
        callbacks: { label: ctx => ` ${ctx.parsed.y} complaints` }
      }},
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { font: { size: 11 } } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, beginAtZero: true, ticks: { stepSize: 1 } }
      },
    }
  });
}

function buildStatusChart(data) {
  const ctx = document.getElementById('statusChart');
  if (!ctx || !data.length) return;

  const colors = data.map(d => STATUS_COLORS[d.status] || '#8892b0');

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.status),
      datasets: [{
        data: data.map(d => d.count),
        backgroundColor: colors.map(c => c + 'cc'),
        borderColor: colors,
        borderWidth: 2,
        hoverBorderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: { display: true, position: 'bottom', labels: { padding: 16, usePointStyle: true, pointStyleWidth: 10, font: { size: 12 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} complaints` } }
      },
    }
  });
}

function buildPriorityChart(data) {
  const ctx = document.getElementById('priorityChart');
  if (!ctx || !data.length) return;

  const ordered = ['Low', 'Medium', 'High', 'Critical'];
  const sorted = ordered.map(p => data.find(d => d.priority === p) || { priority: p, count: 0 });
  const colors = sorted.map(d => PRIORITY_COLORS[d.priority] || '#8892b0');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: sorted.map(d => d.priority),
      datasets: [{
        data: sorted.map(d => d.count),
        backgroundColor: colors.map(c => c + '99'),
        borderColor: colors,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: {
        callbacks: { label: ctx => ` ${ctx.parsed.x} complaints` }
      }},
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.06)' }, beginAtZero: true },
        y: { grid: { color: 'rgba(255,255,255,0.04)' } }
      },
    }
  });
}

function buildTrendChart(data) {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;

  // Format month labels
  const labels = data.map(d => {
    const [y, m] = d.month.split('-');
    return new Date(y, m - 1).toLocaleString('en', { month: 'short', year: '2-digit' });
  });

  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Complaints',
        data: data.map(d => d.count),
        borderColor: CHART_COLORS.accent,
        backgroundColor: 'rgba(108,99,255,0.12)',
        borderWidth: 3,
        pointBackgroundColor: CHART_COLORS.accent,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 9,
        fill: true,
        tension: 0.45,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: {
        callbacks: { label: ctx => ` ${ctx.parsed.y} complaints` }
      }},
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, beginAtZero: true, ticks: { stepSize: 1 } }
      },
    }
  });
}

/* ══════════════════════════════════════════
   FORM VALIDATION & SUBMIT SPINNER
══════════════════════════════════════════ */
const submitForm = document.getElementById('complaintForm');
if (submitForm) {
  submitForm.addEventListener('submit', function (e) {
    let valid = true;
    
    // Validate required fields
    ['title', 'category', 'priority'].forEach(name => {
      const field = submitForm.querySelector(`[name="${name}"]`);
      if (field) {
        if (field.type === 'radio') {
          const checked = submitForm.querySelector(`[name="${name}"]:checked`);
          if (!checked) valid = false;
        } else if (!field.value.trim()) {
          valid = false;
          field.classList.add('error');
          field.addEventListener('input', () => field.classList.remove('error'), { once: true });
        }
      }
    });

    if (!valid) {
      e.preventDefault();
      showToast('Please fill in all required fields.', 'error');
      return;
    }

    // Add loading state
    const btn = document.getElementById('submitBtn');
    if (btn) {
      btn.classList.add('btn-loading');
      btn.disabled = true;
      const textSpan = btn.querySelector('.btn-text');
      if (textSpan) {
        textSpan.textContent = 'Submitting...';
      }
    }
  });
}
