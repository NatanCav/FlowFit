"""
Auth - Sistema de Autenticação e Autorização
Gerencia login, logout e controle de acesso
"""

from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask import request, jsonify

# Chave secreta para JWT (em produção, use variável de ambiente)
SECRET_KEY = 'sua-chave-secreta-aqui-mude-em-producao'

# ==================== FUNÇÕES DE USUÁRIO ====================

def criar_usuario(nome, email, senha, tipo='operador'):
    """
    Cria um novo usuário no sistema
    Tipos: 'admin' ou 'operador'
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        senha_hash = generate_password_hash(senha)
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha_hash, tipo)
            VALUES (?, ?, ?, ?)
        ''', (nome, email, senha_hash, tipo))
        
        conn.commit()
        usuario_id = cursor.lastrowid
        conn.close()
        return {"success": True, "id": usuario_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": "Email já cadastrado"}

def listar_usuarios():
    """
    Lista todos os usuários do sistema
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, email, tipo, ativo, data_criacao, ultimo_acesso
        FROM usuarios 
        WHERE ativo = 1
        ORDER BY nome
    ''')
    
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return usuarios

def obter_usuario(usuario_id):
    """
    Obtém dados de um usuário específico
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, email, tipo, ativo, data_criacao, ultimo_acesso
        FROM usuarios 
        WHERE id = ?
    ''', (usuario_id,))
    
    usuario = cursor.fetchone()
    conn.close()
    
    return dict(usuario) if usuario else None

def atualizar_usuario(usuario_id, nome, email, tipo, senha=None):
    """
    Atualiza dados de um usuário
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if senha:
            senha_hash = generate_password_hash(senha)
            cursor.execute('''
                UPDATE usuarios 
                SET nome = ?, email = ?, tipo = ?, senha_hash = ?
                WHERE id = ?
            ''', (nome, email, tipo, senha_hash, usuario_id))
        else:
            cursor.execute('''
                UPDATE usuarios 
                SET nome = ?, email = ?, tipo = ?
                WHERE id = ?
            ''', (nome, email, tipo, usuario_id))
        
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": "Email já cadastrado para outro usuário"}

def deletar_usuario(usuario_id):
    """
    Desativa um usuário (soft delete)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE usuarios SET ativo = 0 WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()
    
    return {"success": True}

# ==================== AUTENTICAÇÃO ====================

def fazer_login(email, senha):
    """
    Autentica um usuário e retorna token JWT
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, email, senha_hash, tipo 
        FROM usuarios 
        WHERE email = ? AND ativo = 1
    ''', (email,))
    
    usuario = cursor.fetchone()
    
    if not usuario:
        conn.close()
        return {"success": False, "error": "Usuário não encontrado"}
    
    # Verifica a senha
    if not check_password_hash(usuario['senha_hash'], senha):
        conn.close()
        return {"success": False, "error": "Senha incorreta"}
    
    # Atualiza último acesso
    cursor.execute('''
        UPDATE usuarios 
        SET ultimo_acesso = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (usuario['id'],))
    conn.commit()
    
    # Registra no histórico
    cursor.execute('''
        INSERT INTO historico (usuario_id, acao, descricao)
        VALUES (?, ?, ?)
    ''', (usuario['id'], 'LOGIN', f'Usuário {usuario["nome"]} fez login'))
    conn.commit()
    conn.close()
    
    # Gera token JWT
    token = gerar_token(usuario['id'], usuario['email'], usuario['tipo'])
    
    return {
        "success": True,
        "token": token,
        "usuario": {
            "id": usuario['id'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "tipo": usuario['tipo']
        }
    }

def gerar_token(usuario_id, email, tipo):
    """
    Gera um token JWT para o usuário
    """
    payload = {
        'usuario_id': usuario_id,
        'email': email,
        'tipo': tipo,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)  # Token expira em 8 horas
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verificar_token(token):
    """
    Verifica se um token JWT é válido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {"success": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"success": False, "error": "Token expirado"}
    except jwt.InvalidTokenError:
        return {"success": False, "error": "Token inválido"}

# ==================== DECORADOR DE AUTENTICAÇÃO ====================

def requer_autenticacao(f):
    """
    Decorador que verifica se o usuário está autenticado
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "Token não fornecido"}), 401
        
        # Remove 'Bearer ' do token se existir
        if token.startswith('Bearer '):
            token = token[7:]
        
        resultado = verificar_token(token)
        
        if not resultado['success']:
            return jsonify({"error": resultado['error']}), 401
        
        # Adiciona dados do usuário à requisição
        request.usuario = resultado['payload']
        
        return f(*args, **kwargs)
    
    return decorated

def requer_admin(f):
    """
    Decorador que verifica se o usuário é administrador
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "Token não fornecido"}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        resultado = verificar_token(token)
        
        if not resultado['success']:
            return jsonify({"error": resultado['error']}), 401
        
        if resultado['payload']['tipo'] != 'admin':
            return jsonify({"error": "Acesso negado. Apenas administradores."}), 403
        
        request.usuario = resultado['payload']
        
        return f(*args, **kwargs)
    
    return decorated

# ==================== HISTÓRICO ====================

def registrar_historico(usuario_id, acao, descricao):
    """
    Registra uma ação no histórico do sistema
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO historico (usuario_id, acao, descricao)
        VALUES (?, ?, ?)
    ''', (usuario_id, acao, descricao))
    
    conn.commit()
    conn.close()

def obter_historico(limite=50):
    """
    Obtém o histórico de ações do sistema
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT h.*, u.nome as usuario_nome
        FROM historico h
        JOIN usuarios u ON h.usuario_id = u.id
        ORDER BY h.data_acao DESC
        LIMIT ?
    ''', (limite,))
    
    historico = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return historico