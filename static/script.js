
let emails = initialEmails || [];

// Create floating particles for background animation
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;

    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 20 + 's';
        particle.style.animationDuration = (15 + Math.random() * 10) + 's';
        particlesContainer.appendChild(particle);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    renderEmails();
});

function logout() {
    window.location.href = '/logout';
}

function renderEmails() {
    const list = document.getElementById('emailList');
    list.innerHTML = '';
    emails.forEach((email, index) => {
        const div = document.createElement('div');
        div.className = 'email-item';
        div.innerHTML = `
            <span>${email}</span>
            <div class="email-actions">
                <button onclick="removeEmail(${index})">&times;</button>
            </div>
        `;
        list.appendChild(div);
    });
}

function addEmail() {
    const input = document.getElementById('newEmail');
    const email = input.value.trim();
    if (email && validateEmail(email)) {
        if (!emails.includes(email)) {
            emails.push(email);
            renderEmails();
            input.value = '';
        } else {
            alert('Email already exists in list');
        }
    } else {
        alert('Please enter a valid email');
    }
}

function removeEmail(index) {
    emails.splice(index, 1);
    renderEmails();
}

function validateEmail(email) {
    return /\S+@\S+\.\S+/.test(email);
}

async function saveSettings() {
    const priceThreshold = document.getElementById('priceThreshold').value;

    // Get Checked categories
    const checkedCats = [];
    document.querySelectorAll('input[name="category"]:checked').forEach(c => checkedCats.push(c.value));

    const settings = {
        price_threshold: parseInt(priceThreshold),
        emails: emails,
        categories: checkedCats,
        currency: "INR" // Fixed for now based on prev request
    };

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        const data = await res.json();
        alert(data.message);
    } catch (e) {
        alert('Failed to save settings');
    }
}

async function runScraper() {
    const btn = document.getElementById('runBtn');
    const status = document.getElementById('statusMessage');
    const consoleDiv = document.getElementById('consoleOutput');
    const gamesList = document.getElementById('foundGamesList');
    const countTotal = document.getElementById('countTotal');
    const countProcessed = document.getElementById('countProcessed');

    // Reset UI
    btn.disabled = true;
    btn.innerText = 'Running...';
    status.innerText = 'Checking for games...';
    status.style.color = '#666';
    if (consoleDiv) consoleDiv.innerHTML = '';
    if (gamesList) gamesList.innerHTML = '';
    if (countTotal) countTotal.innerText = '0';
    if (countProcessed) countProcessed.innerText = '0';

    // Connect to SSE
    const evtSource = new EventSource("/api/stream_run");

    evtSource.onmessage = function (event) {
        let data;
        try {
            data = JSON.parse(event.data);
        } catch (e) { return; }

        if (data.type === 'log') {
            if (consoleDiv) {
                const p = document.createElement('p');
                p.innerText = `> ${data.message}`;

                // Color coding
                if (data.level === 'error') p.className = 'log-error';
                else if (data.level === 'warning') p.className = 'log-warning';
                else if (data.level === 'success') p.className = 'log-success';
                else p.className = 'log-info';

                consoleDiv.appendChild(p);
                consoleDiv.scrollTop = consoleDiv.scrollHeight;
            }
        }
        else if (data.type === 'progress') {
            // Check if processed is number to avoid 0 overwriting non-zero if packet is partial
            if (valCheck(data.processed) && countProcessed) countProcessed.innerText = data.processed;
            if (valCheck(data.total) && countTotal) countTotal.innerText = data.total;
        }
        if (data.type === 'found') {
            const g = data.game;
            // Add to global list for filtering
            allFoundGames.push(g);

            // Re-run filter to update view (or just add if no filter active, but this is safer)
            filterGames();
        }
        else if (data.type === 'status') {
            status.innerText = data.status === 'success' ? 'Run Complete!' : 'Run Failed!';
            status.style.color = data.status === 'success' ? 'green' : 'red';
        }
        else if (data.type === 'complete') {
            evtSource.close();
            btn.disabled = false;
            btn.innerText = 'Run Notifier Now';
        }
        else if (data.type === 'error') {
            if (consoleDiv) {
                const p = document.createElement('p');
                p.innerText = `ERROR: ${data.message}`;
                p.style.color = 'red';
                consoleDiv.appendChild(p);
                consoleDiv.scrollTop = consoleDiv.scrollHeight;
            }
        }
    };

    evtSource.onerror = function () {
        console.error("EventSource failed.");
        evtSource.close();
        btn.disabled = false;
        btn.innerText = 'Run Notifier Now';
    };
}

// Basic validation helper
function valCheck(val) {
    return typeof val === 'number';
}

async function saveSettings() {
    const settings = {
        emails: emails,
        currency: "INR"
    };

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        const data = await res.json();
        alert(data.message);
    } catch (e) {
        alert('Failed to save settings');
    }
}

// Client-side filtering/sorting
let allFoundGames = []; // Store games for filtering

function filterGames() {
    const search = document.getElementById('gameSearch').value.toLowerCase();
    const sortMode = document.getElementById('gameSort').value;
    const container = document.getElementById('foundGamesList');

    if (!container) return;

    // Filter
    let filtered = allFoundGames.filter(g => {
        return g.title.toLowerCase().includes(search);
    });

    // Sort
    if (sortMode === 'name') {
        filtered.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortMode === 'price_asc') {
        filtered.sort((a, b) => {
            let pa = a.is_free ? 0 : a.discounted_price; // Rough sort
            let pb = b.is_free ? 0 : b.discounted_price;
            // Clean up non-numeric strings if any (e.g. currency symbols) - for now assume comparable
            return (a.is_free ? 0 : 1) - (b.is_free ? 0 : 1); // Free first?
        });
        // Better sort if we parsed prices, but efficient enough: Put Free first
        filtered.sort((a, b) => {
            // Parse price if possible, or just treat "Free" as 0
            let getP = (item) => item.is_free ? 0 : parseFloat(String(item.discounted_price).replace(/[^0-9.]/g, '')) || 999999;
            return getP(a) - getP(b);
        });
    } else if (sortMode === 'price_desc') {
        filtered.sort((a, b) => {
            let getP = (item) => item.is_free ? 0 : parseFloat(String(item.discounted_price).replace(/[^0-9.]/g, '')) || 999999;
            return getP(b) - getP(a);
        });
    }

    // Render
    container.innerHTML = '';
    filtered.forEach(g => {
        const card = document.createElement('a');
        card.href = g.url;
        card.target = "_blank";
        card.className = 'game-card-link';
        card.style.textDecoration = 'none';
        card.style.color = 'inherit';

        let price = g.discounted_price;
        if (g.is_free) price = 'FREE';

        card.innerHTML = `
            <div class="game-card-small">
                <div style="position:relative;">
                    <img src="${g.image_url}" alt="${g.title}">
                    <span class="price-tag" style="position:absolute; bottom:5px; right:5px;">${price}</span>
                </div>
                <div class="info">
                    <h4>${g.title}</h4>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// ... existing runScraper ...
// Ensure we update allFoundGames in runScraper
