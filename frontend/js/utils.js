
/**
 * UTILS.JS - Funções Utilitárias do Sistema
 * Contém funções auxiliares reutilizáveis
 */

// URL base da API
const API_URL = 'http://localhost:5000/api';

/**
 * Formata valor para moeda brasileira (R$)
 * @param {number} valor - Valor numérico
 * @returns {string} Valor formatado
 */
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

/**
 * Formata data no padrão brasileiro (DD/MM/AAAA)
 * @param {string} data - Data no formato ISO (AAAA-MM-DD)
 * @returns {string} Data formatada
 */
function formatarData(data) {
    if (!data) return '-';
    const [ano, mes, dia] = data.split('-');
    return `${dia}/${mes}/${ano}`;
}

/**
 * Converte data brasileira para formato ISO
 * @param {string} data - Data no formato DD/MM/AAAA
 * @returns {string} Data no formato AAAA-MM-DD
 */
function dataParaISO(data) {
    const [dia, mes, ano] = data.split('/');
    return `${ano}-${mes}-${dia}`;
}

/**
 * Formata CPF (000.000.000-00)
 * @param {string} cpf - CPF sem formatação
 * @returns {string} CPF formatado
 */
function formatarCPF(cpf) {
    if (!cpf) return '';
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

/**
 * Formata telefone ((00) 00000-0000)
 * @param {string} telefone - Telefone sem formatação
 * @returns {string} Telefone formatado
 */
function formatarTelefone(telefone) {
    if (!telefone) return '';
    telefone = telefone.replace(/\D/g, '');
    if (telefone.length === 11) {
        return telefone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
    return telefone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
}

/**
 * Calcula dias entre duas datas
 * @param {string} dataInicial - Data inicial
 * @param {string} dataFinal - Data final
 * @returns {number} Número de dias
 */
function calcularDiasEntreDatas(dataInicial, dataFinal) {
    const data1 = new Date(dataInicial);
    const data2 = new Date(dataFinal);
    const diffTime = Math.abs(data2 - data1);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

/**
 * Verifica se uma data está vencida
 * @param {string} dataVencimento - Data de vencimento
 * @returns {boolean} True se vencida
 */
function estaVencido(dataVencimento) {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    const vencimento = new Date(dataVencimento);
    return vencimento < hoje;
}

/**
 * Exibe mensagem de alerta
 * @param {string} mensagem - Texto da mensagem
 * @param {string} tipo - Tipo do alerta (success, danger, warning, info)
 */
function mostrarAlerta(mensagem, tipo = 'info') {
    const alertaDiv = document.createElement('div');
    alertaDiv.className = `alert alert-${tipo}`;
    alertaDiv.innerHTML = `
        <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'danger' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${mensagem}</span>
    `;
    
    document.body.appendChild(alertaDiv);
    
    // Remove alerta após 3 segundos
    setTimeout(() => {
        alertaDiv.remove();
    }, 3000);
}

/**
 * Confirma ação com o usuário
 * @param {string} mensagem - Mensagem de confirmação
 * @returns {boolean} True se confirmado
 */
function confirmar(mensagem) {
    return confirm(mensagem);
}

/**
 * Aplica máscara de CPF em input
 * @param {HTMLInputElement} input - Campo de input
 */
function aplicarMascaraCPF(input) {
    input.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, '');
        if (valor.length > 11) valor = valor.substr(0, 11);
        
        if (valor.length > 9) {
            valor = valor.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        } else if (valor.length > 6) {
            valor = valor.replace(/(\d{3})(\d{3})(\d{3})/, '$1.$2.$3');
        } else if (valor.length > 3) {
            valor = valor.replace(/(\d{3})(\d{3})/, '$1.$2');
        }
        
        e.target.value = valor;
    });
}

/**
 * Aplica máscara de telefone em input
 * @param {HTMLInputElement} input - Campo de input
 */
function aplicarMascaraTelefone(input) {
    input.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, '');
        if (valor.length > 11) valor = valor.substr(0, 11);
        
        if (valor.length > 10) {
            valor = valor.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (valor.length > 6) {
            valor = valor.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        } else if (valor.length > 2) {
            valor = valor.replace(/(\d{2})(\d{0,5})/, '($1) $2');
        }
        
        e.target.value = valor;
    });
}

/**
 * Debounce - Atrasa execução de função
 * @param {Function} func - Função a ser executada
 * @param {number} delay - Tempo de atraso em ms
 * @returns {Function} Função com debounce
 */
function debounce(func, delay = 300) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}