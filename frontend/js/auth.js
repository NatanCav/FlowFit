/**
 * AUTH.JS - Sistema de Autenticação Frontend
 * Gerencia login, logout e sessão do usuário
 */

/**
 * Salva token no localStorage
 * @param {string} token - Token JWT
 */
function salvarToken(token) {
    localStorage.setItem('token', token);
}

/**
 * Obtém token do localStorage
 * @returns {string|null} Token ou null
 */
function obterToken() {
    return localStorage.getItem('token');
}

/**
 * Remove token do localStorage
 */
function removerToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
}

/**
 * Salva dados do usuário no localStorage
 * @param {Object} usuario - Dados do usuário
 */
function salvarUsuario(usuario) {
    localStorage.setItem('usuario', JSON.stringify(usuario));
}

/**
 * Obtém dados do usuário do localStorage
 * @returns {Object|null} Dados do usuário ou null
 */
function obterUsuario() {
    const usuario = localStorage.getItem('usuario');
    return usuario ? JSON.parse(usuario) : null;
}

/**
 * Verifica se usuário está autenticado
 * @returns {boolean} True se autenticado
 */
function estaAutenticado() {
    return obterToken() !== null;
}

/**
 * Verifica se usuário é administrador
 * @returns {boolean} True se for admin
 */
function ehAdmin() {
    const usuario = obterUsuario();
    return usuario && usuario.tipo === 'admin';
}

/**
 * Faz logout e redireciona para login
 */
function logout() {
    removerToken();
    window.location.href = 'login.html';
}

/**
 * Verifica autenticação e redireciona se necessário
 * Deve ser chamada em todas as páginas protegidas
 */
function verificarAutenticacao() {
    if (!estaAutenticado()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * Faz requisição autenticada à API
 * @param {string} url - URL da API
 * @param {Object} options - Opções do fetch
 * @returns {Promise} Resposta da API
 */
async function fetchAuth(url, options = {}) {
    const token = obterToken();
    
    // Adiciona token no header
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        // Se receber 401 (não autorizado), faz logout
        if (response.status === 401) {
            logout();
            throw new Error('Sessão expirada');
        }
        
        return response;
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

/**
 * Inicializa informações do usuário no header
 */
function inicializarInfoUsuario() {
    const usuario = obterUsuario();
    if (!usuario) return;
    
    const userInfoDiv = document.querySelector('.user-info');
    if (userInfoDiv) {
        userInfoDiv.innerHTML = `
            <span><i class="fas fa-user"></i> ${usuario.nome}</span>
            <span class="badge badge-info">${usuario.tipo === 'admin' ? 'Administrador' : 'Operador'}</span>
            <button class="btn-logout" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i> Sair
            </button>
        `;
    }
}

/**
 * Marca link ativo no menu de navegação
 */
function marcarMenuAtivo() {
    const paginaAtual = window.location.pathname.split('/').pop();
    const links = document.querySelectorAll('.navbar a');
    
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href === paginaAtual) {
            link.classList.add('active');
        }
    });
}