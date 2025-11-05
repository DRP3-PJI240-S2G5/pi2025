// Crime Prediction Web Interface

document.addEventListener('DOMContentLoaded', function() {
    checkModelStatus();
    setupEventListeners();
    loadTodaysDate();
});

function setupEventListeners() {
    const form = document.getElementById('predictionForm');
    form.addEventListener('submit', handlePrediction);
}

function loadTodaysDate() {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0];
    const timeStr = today.toTimeString().split(' ')[0].slice(0, 5);

    document.getElementById('data').value = dateStr;
    document.getElementById('hora').value = timeStr;
}

function loadExample() {
    // Load example data for testing
    document.getElementById('data').value = '2024-11-15';
    document.getElementById('hora').value = '20:00';
    document.getElementById('latitude').value = '-23.550520';
    document.getElementById('longitude').value = '-46.633308';
    document.getElementById('bairro').value = 'Centro';
}

async function handlePrediction(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    // Validate input
    if (!data.data || !data.hora || !data.latitude || !data.longitude) {
        showError('Por favor, preencha todos os campos obrigatórios.');
        return;
    }

    // Show results section and hide error
    document.getElementById('predictionResults').classList.remove('hidden');
    document.getElementById('errorMessage').classList.add('hidden');
    document.getElementById('loadingSpinner').classList.remove('hidden');

    // Show loading state
    showLoading();

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            displayResults(result);
        } else {
            showError(result.error || 'Erro desconhecido');
        }

    } catch (error) {
        console.error('Prediction error:', error);
        showError('Erro ao fazer predição. Verifique se o servidor está rodando.');
    }
}

function showLoading() {
    // Hide loading spinner and show results when done
    document.getElementById('loadingSpinner').classList.add('hidden');

    const crimeResult = document.getElementById('crimeResult');
    const locationResult = document.getElementById('locationResult');
    const categoryResult = document.getElementById('categoryResult');

    if (crimeResult) crimeResult.innerHTML = '<div class="loading-text">Carregando...</div>';
    if (locationResult) locationResult.innerHTML = '<div class="loading-text">Carregando...</div>';
    if (categoryResult) categoryResult.innerHTML = '<div class="loading-text">Carregando...</div>';
}

function displayResults(result) {
    const { predictions, analysis } = result;

    // Display crime prediction
    if (predictions.crime && !predictions.crime.error) {
        displayCrimePrediction(predictions.crime);
    } else {
        document.getElementById('crimeResult').innerHTML =
            `<div class="error-message">Erro: ${predictions.crime?.error || 'Não disponível'}</div>`;
    }

    // Display location prediction
    if (predictions.location && !predictions.location.error) {
        displayLocationPrediction(predictions.location);
    } else {
        document.getElementById('locationResult').innerHTML =
            `<div class="error-message">Erro: ${predictions.location?.error || 'Não disponível'}</div>`;
    }

    // Display category prediction
    if (predictions.category && !predictions.category.error) {
        displayCategoryPrediction(predictions.category);
    } else {
        document.getElementById('categoryResult').innerHTML =
            `<div class="error-message">Erro: ${predictions.category?.error || 'Não disponível'}</div>`;
    }

    // Display analysis details
    displayAnalysisDetails(analysis);
}

function showError(message) {
    document.getElementById('predictionResults').classList.add('hidden');
    document.getElementById('loadingSpinner').classList.add('hidden');

    const errorEl = document.getElementById('errorMessage');
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');
}

function displayAnalysisDetails(analysis) {
    const container = document.getElementById('analysisResult');

    let html = `
        <div class="analysis-item">
            <strong>Data e Hora:</strong> ${analysis.datetime}
        </div>
        <div class="analysis-item">
            <strong>Localização:</strong> ${analysis.location}
        </div>
        <div class="analysis-item">
            <strong>Período do Dia:</strong> ${analysis.period}
        </div>
        <div class="analysis-item">
            <strong>Fim de Semana:</strong> ${analysis.weekend}
        </div>
    `;

    container.innerHTML = html;
}

function displayCrimePrediction(crimeData) {
    const container = document.getElementById('crimeResult');

    const mainPrediction = crimeData.prediction;
    const probabilities = crimeData.probabilities || [];

    let html = `<div class="main-prediction">${mainPrediction}</div>`;

    if (probabilities.length > 0) {
        html += '<div class="probability-list">';
        html += '<strong>Top 3 probabilidades:</strong><br>';

        probabilities.slice(0, 3).forEach((item, index) => {
            const percentage = (item.probability * 100).toFixed(1);
            html += `
                <div class="probability-item">
                    <span>${index + 1}. ${item.label}</span>
                    <span>${percentage}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${percentage}%"></div>
                </div>
            `;
        });

        html += '</div>';
    }

    container.innerHTML = html;
}

function displayLocationPrediction(locationData) {
    const container = document.getElementById('locationResult');

    const mainPrediction = locationData.prediction;
    const probabilities = locationData.probabilities || [];

    let html = `<div class="main-prediction">${mainPrediction}</div>`;

    if (probabilities.length > 0) {
        html += '<div class="probability-list">';
        html += '<strong>Top 3 probabilidades:</strong><br>';

        probabilities.slice(0, 3).forEach((item, index) => {
            const percentage = (item.probability * 100).toFixed(1);
            html += `
                <div class="probability-item">
                    <span>${index + 1}. ${item.label}</span>
                    <span>${percentage}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${percentage}%"></div>
                </div>
            `;
        });

        html += '</div>';
    }

    container.innerHTML = html;
}

function displayCategoryPrediction(categoryData) {
    const container = document.getElementById('categoryResult');

    const mainPrediction = categoryData.prediction;
    const probabilities = categoryData.probabilities || [];

    let html = `<div class="main-prediction">${mainPrediction}</div>`;

    if (probabilities.length > 0) {
        html += '<div class="probability-list">';
        html += '<strong>Todas as categorias:</strong><br>';

        probabilities.forEach((item, index) => {
            const percentage = (item.probability * 100).toFixed(1);
            html += `
                <div class="probability-item">
                    <span>${item.label}</span>
                    <span>${percentage}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${percentage}%"></div>
                </div>
            `;
        });

        html += '</div>';
    }

    container.innerHTML = html;
}

async function checkModelStatus() {
    try {
        const response = await fetch('/api/model-status');
        const status = await response.json();

        const statusEl = document.getElementById('statusText');
        const statusCard = document.getElementById('modelStatus');

        if (status.models_trained) {
            statusEl.textContent = '✅ Modelos carregados e prontos para predição';
            statusCard.className = 'status-card status-success';
        } else {
            statusEl.textContent = '⚠️ Modelos não encontrados. Será necessário treinar.';
            statusCard.className = 'status-card status-warning';
        }
    } catch (error) {
        const statusEl = document.getElementById('statusText');
        const statusCard = document.getElementById('modelStatus');

        statusEl.textContent = '❌ Erro ao verificar status dos modelos';
        statusCard.className = 'status-card status-error';
        console.error('Error checking model status:', error);
    }
}

// Add some additional CSS styles dynamically
const additionalStyles = `
    .analysis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .analysis-item {
        background: white;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #3498db;
    }
    
    .features-used {
        margin-top: 20px;
        padding: 15px;
        background: white;
        border-radius: 8px;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px;
        margin-top: 10px;
        font-size: 0.9em;
    }
    
    .features-grid div {
        background: #f8f9fa;
        padding: 5px 10px;
        border-radius: 4px;
        border: 1px solid #dee2e6;
    }
    
    .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }
    
    .status-item {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    
    .model-files {
        margin-top: 15px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
        font-family: monospace;
        font-size: 0.9em;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
