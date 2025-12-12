// Funções JavaScript principais para o EduQBank

// Carregar questões selecionadas do localStorage
function loadSelectedQuestions() {
    const selected = JSON.parse(localStorage.getItem('selectedQuestions') || '[]');
    updateSelectedCount();
    return selected;
}

// Salvar questões selecionadas no localStorage
function saveSelectedQuestions(questionIds) {
    localStorage.setItem('selectedQuestions', JSON.stringify(questionIds));
    updateSelectedCount();
}

// Adicionar questão à seleção
function addQuestionToSelection(questionId, questionData) {
    const selected = loadSelectedQuestions();
    if (!selected.find(q => q.id === questionId)) {
        selected.push({ id: questionId, ...questionData });
        saveSelectedQuestions(selected);
        renderSelectedQuestions();
    }
}

// Remover questão da seleção
function removeQuestionFromSelection(questionId) {
    const selected = loadSelectedQuestions();
    const filtered = selected.filter(q => q.id !== questionId);
    saveSelectedQuestions(filtered);
    renderSelectedQuestions();
}

// Atualizar contador de questões selecionadas
function updateSelectedCount() {
    const selected = loadSelectedQuestions();
    const count = selected.length;
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = count;
    }
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = count === 0;
    }
}

// Renderizar questões selecionadas
function renderSelectedQuestions() {
    const container = document.getElementById('selectedQuestionsContainer');
    if (!container) return;
    
    const selected = loadSelectedQuestions();
    
    if (selected.length === 0) {
        container.innerHTML = `
            <p class="text-muted">Nenhuma questão selecionada ainda. 
                <a href="/questoes/">Clique aqui para buscar questões</a>
            </p>
        `;
        return;
    }
    
    let html = '<div class="row g-3">';
    selected.forEach(q => {
        html += `
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="mb-2">Questão #${q.id}</h6>
                                ${q.area ? `<span class="badge bg-primary">${q.area}</span>` : ''}
                                ${q.ano ? `<span class="badge bg-info">${q.ano}</span>` : ''}
                            </div>
                            <button type="button" class="btn btn-sm btn-outline-danger" 
                                    onclick="removeQuestionFromSelection(${q.id})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <input type="hidden" name="question_ids" value="${q.id}">
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Se estiver na página de criar prova, renderizar questões selecionadas
    if (document.getElementById('selectedQuestionsContainer')) {
        renderSelectedQuestions();
    }
    
    // Adicionar botões "Adicionar à Prova" nas questões
    document.querySelectorAll('.question-card').forEach(card => {
        const questionId = card.dataset.questionId;
        if (questionId && !card.querySelector('.add-to-test-btn')) {
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-success add-to-test-btn';
            btn.innerHTML = '<i class="fas fa-plus me-1"></i>Adicionar à Prova';
            btn.onclick = function() {
                const area = card.querySelector('.badge.bg-primary')?.textContent || '';
                const ano = card.querySelector('.badge.bg-info')?.textContent || '';
                addQuestionToSelection(parseInt(questionId), { area, ano });
                btn.innerHTML = '<i class="fas fa-check me-1"></i>Adicionada';
                btn.disabled = true;
            };
            const actionsDiv = card.querySelector('.mt-2');
            if (actionsDiv) {
                actionsDiv.appendChild(btn);
            }
        }
    });
});

// Funções para seleção em massa
function selectAll() {
    document.querySelectorAll('input[name="question_ids"]').forEach(cb => {
        cb.checked = true;
    });
    updateSelectedCount();
}

function deselectAll() {
    document.querySelectorAll('input[name="question_ids"]').forEach(cb => {
        cb.checked = false;
    });
    updateSelectedCount();
}

// Auto-submit em busca com debounce
let searchTimeout;
if (document.getElementById('search')) {
    document.getElementById('search').addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const form = document.getElementById('filterForm');
            if (form) form.submit();
        }, 500);
    });
}


