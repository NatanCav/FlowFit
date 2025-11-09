"""
Models - Modelos de Dados e Operações no Banco
Contém todas as funções para manipular clientes e pagamentos
"""

from database import get_connection
from datetime import datetime, date

# ==================== OPERAÇÕES DE CLIENTES ====================

def criar_cliente(nome, email, telefone, cpf, endereco='', observacoes=''):
    """
    Cria um novo cliente no banco de dados
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO clientes (nome, email, telefone, cpf, endereco, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, email, telefone, cpf, endereco, observacoes))
        
        conn.commit()
        cliente_id = cursor.lastrowid
        conn.close()
        return {"success": True, "id": cliente_id}
    except Exception as e:
        conn.close()
        return {"success": False, "error": "CPF já cadastrado"}

def listar_clientes(busca=None):
    """
    Lista todos os clientes ou filtra por nome/CPF
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if busca:
        cursor.execute('''
            SELECT * FROM clientes 
            WHERE (nome LIKE ? OR cpf LIKE ?) AND ativo = 1
            ORDER BY nome
        ''', (f'%{busca}%', f'%{busca}%'))
    else:
        cursor.execute('SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome')
    
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clientes

def obter_cliente(cliente_id):
    """
    Obtém um cliente específico por ID com estatísticas
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Dados do cliente
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
    cliente = cursor.fetchone()
    
    if not cliente:
        conn.close()
        return None
    
    cliente_dict = dict(cliente)
    
    # Estatísticas de pagamentos
    cursor.execute('''
        SELECT 
            COUNT(*) as total_pagamentos,
            SUM(CASE WHEN status = 'pago' THEN 1 ELSE 0 END) as pagamentos_pagos,
            SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) as pagamentos_pendentes,
            SUM(CASE WHEN status = 'pendente' THEN valor ELSE 0 END) as valor_pendente
        FROM pagamentos
        WHERE cliente_id = ?
    ''', (cliente_id,))
    
    stats = dict(cursor.fetchone())
    cliente_dict['estatisticas'] = stats
    
    conn.close()
    return cliente_dict

def atualizar_cliente(cliente_id, nome, email, telefone, cpf, endereco='', observacoes=''):
    """
    Atualiza os dados de um cliente
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE clientes 
            SET nome = ?, email = ?, telefone = ?, cpf = ?, endereco = ?, observacoes = ?
            WHERE id = ?
        ''', (nome, email, telefone, cpf, endereco, observacoes, cliente_id))
        
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        conn.close()
        return {"success": False, "error": "CPF já cadastrado para outro cliente"}

def deletar_cliente(cliente_id):
    """
    Desativa um cliente (soft delete)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE clientes SET ativo = 0 WHERE id = ?', (cliente_id,))
    conn.commit()
    conn.close()
    
    return {"success": True}

# ==================== OPERAÇÕES DE PAGAMENTOS ====================

def criar_pagamento(cliente_id, valor, vencimento, descricao, usuario_id=None):
    """
    Cria um novo pagamento para um cliente
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO pagamentos (cliente_id, valor, vencimento, descricao, status, usuario_registro_id)
        VALUES (?, ?, ?, ?, 'pendente', ?)
    ''', (cliente_id, valor, vencimento, descricao, usuario_id))
    
    conn.commit()
    pagamento_id = cursor.lastrowid
    conn.close()
    
    return {"success": True, "id": pagamento_id}

def listar_pagamentos(cliente_id=None, status=None, mes=None):
    """
    Lista pagamentos com filtros opcionais
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT p.*, c.nome as cliente_nome, c.cpf as cliente_cpf, c.telefone as cliente_telefone
        FROM pagamentos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE 1=1
    '''
    params = []
    
    if cliente_id:
        query += ' AND p.cliente_id = ?'
        params.append(cliente_id)
    
    if status:
        query += ' AND p.status = ?'
        params.append(status)
    
    if mes:
        query += ' AND strftime("%Y-%m", p.vencimento) = ?'
        params.append(mes)
    
    query += ' ORDER BY p.vencimento DESC'
    
    cursor.execute(query, params)
    pagamentos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return pagamentos

def obter_historico_pagamentos(cliente_id):
    """
    Obtém o histórico completo de pagamentos de um cliente
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, u.nome as usuario_nome
        FROM pagamentos p
        LEFT JOIN usuarios u ON p.usuario_registro_id = u.id
        WHERE p.cliente_id = ?
        ORDER BY p.vencimento DESC
    ''', (cliente_id,))
    
    pagamentos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return pagamentos

def registrar_pagamento(pagamento_id, metodo_pagamento):
    """
    Registra um pagamento como pago
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    data_hoje = date.today().isoformat()
    
    cursor.execute('''
        UPDATE pagamentos 
        SET status = 'pago', data_pagamento = ?, metodo_pagamento = ?
        WHERE id = ?
    ''', (data_hoje, metodo_pagamento, pagamento_id))
    
    conn.commit()
    conn.close()
    
    return {"success": True}

def cancelar_pagamento(pagamento_id):
    """
    Cancela um pagamento
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE pagamentos 
        SET status = 'cancelado'
        WHERE id = ?
    ''', (pagamento_id,))
    
    conn.commit()
    conn.close()
    
    return {"success": True}

def deletar_pagamento(pagamento_id):
    """
    Deleta permanentemente um pagamento
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM pagamentos WHERE id = ?', (pagamento_id,))
    conn.commit()
    conn.close()
    
    return {"success": True}

# ==================== RELATÓRIOS E DASHBOARD ====================

def obter_estatisticas():
    """
    Obtém estatísticas gerais do sistema
    Separa corretamente pagamentos pendentes (no prazo) e vencidos (atrasados)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    data_hoje = date.today().isoformat()
    mes_atual = datetime.now().strftime('%Y-%m')
    
    # Total de clientes ativos
    cursor.execute('SELECT COUNT(*) as total FROM clientes WHERE ativo = 1')
    total_clientes = cursor.fetchone()['total']
    
    # Pagamentos pendentes DENTRO DO PRAZO (vencimento >= hoje)
    cursor.execute('''
        SELECT COUNT(*) as total 
        FROM pagamentos 
        WHERE status = "pendente" AND vencimento >= ?
    ''', (data_hoje,))
    pagamentos_pendentes = cursor.fetchone()['total']
    
    # Pagamentos VENCIDOS (vencimento < hoje)
    cursor.execute('''
        SELECT COUNT(*) as total 
        FROM pagamentos 
        WHERE status = "pendente" AND vencimento < ?
    ''', (data_hoje,))
    pagamentos_vencidos = cursor.fetchone()['total']
    
    # Valor pendente DENTRO DO PRAZO
    cursor.execute('''
        SELECT COALESCE(SUM(valor), 0) as total 
        FROM pagamentos 
        WHERE status = "pendente" AND vencimento >= ?
    ''', (data_hoje,))
    valor_pendente = cursor.fetchone()['total']
    
    # Valor VENCIDO (em atraso)
    cursor.execute('''
        SELECT COALESCE(SUM(valor), 0) as total 
        FROM pagamentos 
        WHERE status = "pendente" AND vencimento < ?
    ''', (data_hoje,))
    valor_vencido = cursor.fetchone()['total']
    
    # Valor total em aberto (pendentes + vencidos)
    valor_em_aberto = valor_pendente + valor_vencido
    
    # Valor recebido no mês atual
    cursor.execute('''
        SELECT COALESCE(SUM(valor), 0) as total 
        FROM pagamentos 
        WHERE status = "pago" AND data_pagamento LIKE ?
    ''', (f'{mes_atual}%',))
    valor_recebido_mes = cursor.fetchone()['total']
    
    # Clientes que pagaram este mês
    cursor.execute('''
        SELECT COUNT(DISTINCT cliente_id) as total
        FROM pagamentos 
        WHERE status = "pago" AND data_pagamento LIKE ?
    ''', (f'{mes_atual}%',))
    clientes_pagaram_mes = cursor.fetchone()['total']
    
    conn.close()
    
    return {
        "total_clientes": total_clientes,
        "pagamentos_pendentes": pagamentos_pendentes,  # No prazo
        "pagamentos_vencidos": pagamentos_vencidos,    # Atrasados
        "valor_pendente": valor_pendente,              # Valor no prazo
        "valor_vencido": valor_vencido,                # Valor atrasado
        "valor_em_aberto": valor_em_aberto,            # Total (pendente + vencido)
        "valor_recebido_mes": valor_recebido_mes,
        "clientes_pagaram_mes": clientes_pagaram_mes
    }

def obter_inadimplentes():
    """
    Lista clientes com pagamentos vencidos
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    data_hoje = date.today().isoformat()
    
    cursor.execute('''
        SELECT c.id, c.nome, c.telefone, c.email,
               COUNT(p.id) as qtd_pendencias,
               SUM(p.valor) as valor_total,
               MIN(p.vencimento) as vencimento_mais_antigo
        FROM clientes c
        JOIN pagamentos p ON c.id = p.cliente_id
        WHERE p.status = 'pendente' AND p.vencimento < ?
        GROUP BY c.id
        ORDER BY vencimento_mais_antigo
    ''', (data_hoje,))
    
    inadimplentes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return inadimplentes

def obter_clientes_pagaram_mes():
    """
    Lista clientes que pagaram no mês atual
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    mes_atual = datetime.now().strftime('%Y-%m')
    
    cursor.execute('''
        SELECT c.id, c.nome, c.telefone,
               COUNT(p.id) as qtd_pagamentos,
               SUM(p.valor) as valor_total,
               MAX(p.data_pagamento) as ultimo_pagamento
        FROM clientes c
        JOIN pagamentos p ON c.id = p.cliente_id
        WHERE p.status = 'pago' AND p.data_pagamento LIKE ?
        GROUP BY c.id
        ORDER BY c.nome
    ''', (f'{mes_atual}%',))
    
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return clientes