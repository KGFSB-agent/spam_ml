let authToken = null;

async function login() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();
    
    if (!email || !password) {
        alert('Please fill all fields');
        return;
    }

    const response = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({
            username: email,
            password: password,
            grant_type: 'password'
        })
    });

    if(response.ok) {
        const data = await response.json();
        authToken = data.access_token;
        showMainInterface();
        loadUserData();
        loadAnalytics();
    } else {
        const error = await response.json();
        alert(`Login failed: ${error.detail}`);
    }
}

async function register() {
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    const response = await fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    if(response.ok) {
        alert('Registration successful! Please login');
        showTab('login');
    } else {
        alert('Registration failed');
    }
}

async function addCredits() {
    const amount = parseFloat(document.getElementById('credit-amount').value);
    
    if (isNaN(amount) || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/add_credits', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ amount })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add credits');
        }

        const result = await response.json();
        alert(result.message);
        loadUserData();
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function analyze() {
    const text = document.getElementById('input-text').value;
    const model = document.getElementById('model-select').value;
    
    const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
            text: text,
            model_type: model
        })
    });

    if(response.ok) {
        const result = await response.json();
        showResult(result);
        loadUserData();
        loadHistory();
        loadAnalytics();
    } else {
        alert('Analysis failed');
    }
}

function showResult(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.className = result.is_spam ? 'spam' : 'not-spam';
    resultDiv.innerHTML = `
        Result: ${result.is_spam ? 'SPAM' : 'Not Spam'}<br>
        Remaining Balance: ${result.remaining_balance} credits
    `;
}

async function loadUserData() {
    const response = await fetch('http://localhost:8000/balance', {
        headers: {'Authorization': `Bearer ${authToken}`}
    });
    
    if(response.ok) {
        const data = await response.json();
        document.getElementById('user-balance').textContent = 
            `Balance: ${data.balance} credits`;
    }
}

async function loadHistory() {
    const response = await fetch('http://localhost:8000/prediction_history', {
        headers: {'Authorization': `Bearer ${authToken}`}
    });
    
    if(response.ok) {
        const history = await response.json();
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = history.map(item => `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-date">${new Date(item.created_at).toLocaleString()}</span>
                    <span class="history-model">${item.model_type}</span>
                    <span class="${item.is_spam ? 'spam' : 'not-spam'}">${item.is_spam ? 'SPAM' : 'Clean'}</span>
                </div>
                <div class="history-text">${item.text.slice(0, 80)}${item.text.length > 80 ? '...' : ''}</div>
            </div>
        `).join('');
        loadAnalytics();
    }
}

async function loadAnalytics() {
    const historyResponse = await fetch('http://localhost:8000/prediction_history', {
        headers: {'Authorization': `Bearer ${authToken}`}
    });
    
    if (historyResponse.ok) {
        const history = await historyResponse.json();
        document.getElementById('total-predictions').textContent = history.length;
        document.getElementById('total-spam').textContent = 
            history.filter(item => item.is_spam).length;
        document.getElementById('total-credits').textContent = 
            history.reduce((sum, item) => sum + item.cost, 0);
    }
}

function logout() {
    authToken = null;
    document.getElementById('main-interface').style.display = 'none';
    document.getElementById('auth-section').style.display = 'block';
}

function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('#login-form, #register-form').forEach(form => 
        form.style.display = 'none'
    );
    
    if(tabName === 'login') {
        document.getElementById('login-form').style.display = 'block';
        document.querySelector('.tab:nth-child(1)').classList.add('active');
    } else {
        document.getElementById('register-form').style.display = 'block';
        document.querySelector('.tab:nth-child(2)').classList.add('active');
    }
}

function showMainInterface() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('main-interface').style.display = 'block';
    document.getElementById('user-email').textContent = 
        document.getElementById('login-email').value;
}
