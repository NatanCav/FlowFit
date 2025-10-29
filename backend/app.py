"""
App- Servidor Backend da Aplicação
API REST usando Flask para gerenciamento de pagamentos
Inclui sistema de autenticação e autorização
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import database
import models
import auth

# Inicializa o Flask
app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Inicializa o banco de dados
database.init_db()

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    POST /api/auth/login - Faz login no sistema
    Body: {email, senha}
    """
    data = request.json
    resultado = auth.fazer_login(data['email'], data['senha'])
    
    if resultado['success']:
        return jsonify(resultado), 200
    return jsonify(resultado), 401

@app.route('/api/auth/verificar', methods=['GET'])
@auth.requer_autenticacao
def verificar_sessao():
    """
    GET /api/auth/verificar - Verifica se o token é válido
    """
    return jsonify({
        "success": True,
        "usuario": request.usuario
    })

# ==================== ROTAS DE USUÁRIOS ====================

@app.route('/api/usuarios', methods=['GET'])
@auth.requer_admin
def get_usuarios():
    """
    GET /api/usuarios - Lista todos os usuários (apenas admin)
    """
    usuarios = auth.listar_usuarios()
    return jsonify(usuarios)

@app.route('/api/usuarios', methods=['POST'])
@auth.requer_admin
def create_usuario():
    """
    POST /api/usuarios - Cria um novo usuário (apenas admin)
    Body: {nome, email, senha, tipo}
    """
    data = request.json
    resultado = auth.criar_usuario(
        data['nome'],
        data['email'],
        data['senha'],
        data.get('tipo', 'operador')
    )
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'CRIAR_USUARIO',
            f'Criou usuário: {data["nome"]}'
        )
    
    return jsonify(resultado)

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
@auth.requer_admin
def get_usuario(usuario_id):
    """
    GET /api/usuarios/:id - Obtém um usuário específico
    """
    usuario = auth.obter_usuario(usuario_id)
    if usuario:
        return jsonify(usuario)
    return jsonify({"error": "Usuário não encontrado"}), 404

@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
@auth.requer_admin
def update_usuario(usuario_id):
    """
    PUT /api/usuarios/:id - Atualiza um usuário
    Body: {nome, email, tipo, senha (opcional)}
    """
    data = request.json
    resultado = auth.atualizar_usuario(
        usuario_id,
        data['nome'],
        data['email'],
        data['tipo'],
        data.get('senha')
    )
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'ATUALIZAR_USUARIO',
            f'Atualizou usuário ID: {usuario_id}'
        )
    
    return jsonify(resultado)

@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
@auth.requer_admin
def delete_usuario(usuario_id):
    """
    DELETE /api/usuarios/:id - Desativa um usuário
    """
    resultado = auth.deletar_usuario(usuario_id)
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'DELETAR_USUARIO',
            f'Deletou usuário ID: {usuario_id}'
        )
    
    return jsonify(resultado)

# ==================== ROTAS DE CLIENTES ====================

@app.route('/api/clientes', methods=['GET'])
@auth.requer_autenticacao
def get_clientes():
    """
    GET /api/clientes - Lista todos os clientes
    Query params: busca (opcional)
    """
    busca = request.args.get('busca')
    clientes = models.listar_clientes(busca)
    return jsonify(clientes)

@app.route('/api/clientes', methods=['POST'])
@auth.requer_autenticacao
def create_cliente():
    """
    POST /api/clientes - Cria um novo cliente
    Body: {nome, email, telefone, cpf, endereco, observacoes}
    """
    data = request.json
    resultado = models.criar_cliente(
        data['nome'],
        data.get('email', ''),
        data.get('telefone', ''),
        data.get('cpf', ''),
        data.get('endereco', ''),
        data.get('observacoes', '')
    )
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'CRIAR_CLIENTE',
            f'Criou cliente: {data["nome"]}'
        )
    
    return jsonify(resultado)

@app.route('/api/clientes/<int:cliente_id>', methods=['GET'])
@auth.requer_autenticacao
def get_cliente(cliente_id):
    """
    GET /api/clientes/:id - Obtém um cliente específico
    """
    cliente = models.obter_cliente(cliente_id)
    if cliente:
        return jsonify(cliente)
    return jsonify({"error": "Cliente não encontrado"}), 404

@app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
@auth.requer_autenticacao
def update_cliente(cliente_id):
    """
    PUT /api/clientes/:id - Atualiza um cliente
    Body: {nome, email, telefone, cpf, endereco, observacoes}
    """
    data = request.json
    resultado = models.atualizar_cliente(
        cliente_id,
        data['nome'],
        data.get('email', ''),
        data.get('telefone', ''),
        data.get('cpf', ''),
        data.get('endereco', ''),
        data.get('observacoes', '')
    )
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'ATUALIZAR_CLIENTE',
            f'Atualizou cliente ID: {cliente_id}'
        )
    
    return jsonify(resultado)

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
@auth.requer_autenticacao
def delete_cliente(cliente_id):
    """
    DELETE /api/clientes/:id - Desativa um cliente
    """
    resultado = models.deletar_cliente(cliente_id)
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'DELETAR_CLIENTE',
            f'Deletou cliente ID: {cliente_id}'
        )
    
    return jsonify(resultado)

# ==================== ROTAS DE PAGAMENTOS ====================

@app.route('/api/pagamentos', methods=['GET'])
@auth.requer_autenticacao
def get_pagamentos():
    """
    GET /api/pagamentos - Lista pagamentos
    Query params: cliente_id (opcional), status (opcional), mes (opcional)
    """
    cliente_id = request.args.get('cliente_id', type=int)
    status = request.args.get('status')
    mes = request.args.get('mes')
    pagamentos = models.listar_pagamentos(cliente_id, status, mes)
    return jsonify(pagamentos)

@app.route('/api/pagamentos', methods=['POST'])
@auth.requer_autenticacao
def create_pagamento():
    """
    POST /api/pagamentos - Cria um novo pagamento
    Body: {cliente_id, valor, vencimento, descricao}
    """
    data = request.json
    resultado = models.criar_pagamento(
        data['cliente_id'],
        data['valor'],
        data['vencimento'],
        data.get('descricao', ''),
        request.usuario['usuario_id']
    )
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'CRIAR_PAGAMENTO',
            f'Criou pagamento para cliente ID: {data["cliente_id"]}'
        )
    
    return jsonify(resultado)

@app.route('/api/pagamentos/<int:pagamento_id>/pagar', methods=['POST'])
@auth.requer_autenticacao
def pagar_pagamento(pagamento_id):
    """
    POST /api/pagamentos/:id/pagar - Registra um pagamento como pago
    Body: {metodo_pagamento}
    """
    data = request.json
    resultado = models.registrar_pagamento(
        pagamento_id,
        data.get('metodo_pagamento', 'Não informado')
    )
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'REGISTRAR_PAGAMENTO',
            f'Registrou pagamento ID: {pagamento_id}'
        )
    
    return jsonify(resultado)

@app.route('/api/pagamentos/<int:pagamento_id>/cancelar', methods=['POST'])
@auth.requer_autenticacao
def cancelar_pagamento(pagamento_id):
    """
    POST /api/pagamentos/:id/cancelar - Cancela um pagamento
    """
    resultado = models.cancelar_pagamento(pagamento_id)
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'CANCELAR_PAGAMENTO',
            f'Cancelou pagamento ID: {pagamento_id}'
        )
    
    return jsonify(resultado)

@app.route('/api/pagamentos/<int:pagamento_id>', methods=['DELETE'])
@auth.requer_autenticacao
def delete_pagamento(pagamento_id):
    """
    DELETE /api/pagamentos/:id - Deleta um pagamento
    """
    resultado = models.deletar_pagamento(pagamento_id)
    
    if resultado['success']:
        auth.registrar_historico(
            request.usuario['usuario_id'],
            'DELETAR_PAGAMENTO',
            f'Deletou pagamento ID: {pagamento_id}'
        )
    
    return jsonify(resultado)

@app.route('/api/historico/<int:cliente_id>', methods=['GET'])
@auth.requer_autenticacao
def get_historico_cliente(cliente_id):
    """
    GET /api/historico/:cliente_id - Obtém histórico de pagamentos de um cliente
    """
    historico = models.obter_historico_pagamentos(cliente_id)
    return jsonify(historico)

# ==================== ROTAS DE RELATÓRIOS ====================

@app.route('/api/dashboard', methods=['GET'])
@auth.requer_autenticacao
def get_dashboard():
    """
    GET /api/dashboard - Obtém estatísticas gerais
    """
    stats = models.obter_estatisticas()
    return jsonify(stats)

@app.route('/api/inadimplentes', methods=['GET'])
@auth.requer_autenticacao
def get_inadimplentes():
    """
    GET /api/inadimplentes - Lista clientes inadimplentes
    """
    inadimplentes = models.obter_inadimplentes()
    return jsonify(inadimplentes)

@app.route('/api/pagamentos/mes-atual', methods=['GET'])
@auth.requer_autenticacao
def get_pagamentos_mes_atual():
    """
    GET /api/pagamentos/mes-atual - Lista clientes que pagaram este mês
    """
    clientes = models.obter_clientes_pagaram_mes()
    return jsonify(clientes)

@app.route('/api/historico', methods=['GET'])
@auth.requer_admin
def get_historico_sistema():
    """
    GET /api/historico - Obtém histórico de ações do sistema (apenas admin)
    """
    limite = request.args.get('limite', 50, type=int)
    historico = auth.obter_historico(limite)
    return jsonify(historico)

# ==================== ROTA DE TESTE ====================

@app.route('/api/status', methods=['GET'])
def status():
    """
    GET /api/status - Verifica se a API está funcionando
    """
    return jsonify({
        "status": "online",
        "mensagem": "API funcionando corretamente"
    })

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SISTEMA DE GERENCIAMENTO DE PAGAMENTOS")
    print("="*50)
    print("📊 Frontend: Abra o arquivo frontend/login.html no navegador")
    print("🔌 API: http://localhost:5000/api")
    print("="*50)
    print("👤 Usuário padrão:")
    print("   Email: admin@sistema.com")
    print("   Senha: admin123")
    print("="*50 + "\n")
    
    # Inicia o servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)