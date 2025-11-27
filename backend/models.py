# models.py atualizado
from database import get_engine, get_date_format, get_date_diff
from sqlalchemy import text
from datetime import date

def criar_cliente(nome, email, telefone, cpf, endereco='', observacoes=''):
    with get_engine().connect() as conn:
        try:
            dialect = get_engine().dialect.name
            if dialect == 'sqlite':
                conn.execute(text('''
                    INSERT INTO clientes (nome, email, telefone, cpf, endereco, observacoes)
                    VALUES (:nome, :email, :telefone, :cpf, :endereco, :observacoes)
                '''), {'nome': nome, 'email': email, 'telefone': telefone, 'cpf': cpf, 'endereco': endereco, 'observacoes': observacoes})
                result = conn.execute(text('SELECT last_insert_rowid()'))
                cliente_id = result.fetchone()[0]
            else:
                result = conn.execute(text('''
                    INSERT INTO clientes (nome, email, telefone, cpf, endereco, observacoes)
                    VALUES (:nome, :email, :telefone, :cpf, :endereco, :observacoes)
                    RETURNING id
                '''), {'nome': nome, 'email': email, 'telefone': telefone, 'cpf': cpf, 'endereco': endereco, 'observacoes': observacoes})
                cliente_id = result.fetchone()[0]

            conn.commit()
            return {"success": True, "id": cliente_id}
        except Exception as e:
            return {"success": False, "error": "CPF já cadastrado" if 'unique' in str(e).lower() else str(e)}

def listar_clientes(busca=None):
    with get_engine().connect() as conn:
        if busca:
            # ILIKE não existe no SQLite; usa LOWER comparison para compatibilidade
            result = conn.execute(text('''
                SELECT * FROM clientes
                WHERE (LOWER(nome) LIKE LOWER(:busca_nome) OR cpf LIKE :busca_cpf) AND ativo = TRUE
                ORDER BY nome
            '''), {'busca_nome': f'%{busca}%', 'busca_cpf': f'%{busca}%'} )
        else:
            result = conn.execute(text('SELECT * FROM clientes WHERE ativo = TRUE ORDER BY nome'))
        clientes = [dict(row._mapping) for row in result]  # Usa _mapping para dict
        return clientes

def obter_cliente(cliente_id):
    with get_engine().connect() as conn:
        result = conn.execute(text('SELECT * FROM clientes WHERE id = :id AND ativo = TRUE'), {'id': cliente_id})
        cliente = result.fetchone()
        return dict(cliente._mapping) if cliente else None

def atualizar_cliente(cliente_id, dados):
    with get_engine().connect() as conn:
        set_clause = ', '.join(f"{k} = :{k}" for k in dados)
        sql = text(f'UPDATE clientes SET {set_clause} WHERE id = :id')
        params = {**dados, 'id': cliente_id}
        conn.execute(sql, params)
        conn.commit()
        return {"success": True}

def deletar_cliente(cliente_id):
    with get_engine().connect() as conn:
        conn.execute(text('UPDATE clientes SET ativo = FALSE WHERE id = :id'), {'id': cliente_id})
        conn.commit()
        return {"success": True}

def criar_pagamento(cliente_id, valor, vencimento, descricao='', usuario_id=None, observacoes='', metodo=''):
    """Cria um novo pagamento (equivalente ao endpoint /api/pagamentos POST).

    Mantém compatibilidade com a API que chama `models.criar_pagamento(...)`.
    """
    with get_engine().connect() as conn:
        dialect = get_engine().dialect.name
        if dialect == 'sqlite':
            conn.execute(text('''
                INSERT INTO pagamentos (cliente_id, valor, vencimento, descricao, metodo_pagamento, observacoes, usuario_registro_id)
                VALUES (:cliente_id, :valor, :vencimento, :descricao, :metodo, :observacoes, :usuario_id)
            '''), {'cliente_id': cliente_id, 'valor': valor, 'vencimento': vencimento, 'descricao': descricao,
                   'metodo': metodo, 'observacoes': observacoes, 'usuario_id': usuario_id})
            result = conn.execute(text('SELECT last_insert_rowid()'))
            pagamento_id = result.fetchone()[0]
        else:
            result = conn.execute(text('''
                INSERT INTO pagamentos (cliente_id, valor, vencimento, descricao, metodo_pagamento, observacoes, usuario_registro_id)
                VALUES (:cliente_id, :valor, :vencimento, :descricao, :metodo, :observacoes, :usuario_id)
                RETURNING id
            '''), {'cliente_id': cliente_id, 'valor': valor, 'vencimento': vencimento, 'descricao': descricao,
                   'metodo': metodo, 'observacoes': observacoes, 'usuario_id': usuario_id})
            pagamento_id = result.fetchone()[0]
        conn.commit()
        return {"success": True, "id": pagamento_id}

def registrar_pagamento(pagamento_id, metodo_pagamento='Não informado'):
    """Marca um pagamento como pago (usado pelo endpoint /api/pagamentos/:id/pagar).

    Atualiza status, data_pagamento e método de pagamento.
    """
    with get_engine().connect() as conn:
        # Verifica existência
        result = conn.execute(text('SELECT id, status FROM pagamentos WHERE id = :id'), {'id': pagamento_id})
        row = result.fetchone()
        if not row:
            return {"success": False, "error": "Pagamento não encontrado"}

        # Atualiza
        dialect = get_engine().dialect.name
        # Use função de data compatível
        date_expr = "CURRENT_DATE" if dialect != 'sqlite' else "date('now')"
        conn.execute(text(f'''
            UPDATE pagamentos
            SET status = 'pago', data_pagamento = {date_expr}, metodo_pagamento = :metodo
            WHERE id = :id
        '''), {'metodo': metodo_pagamento, 'id': pagamento_id})
        conn.commit()
        return {"success": True}

def cancelar_pagamento(pagamento_id):
    """Marca um pagamento como cancelado."""
    with get_engine().connect() as conn:
        result = conn.execute(text('SELECT id FROM pagamentos WHERE id = :id'), {'id': pagamento_id})
        if not result.fetchone():
            return {"success": False, "error": "Pagamento não encontrado"}
        conn.execute(text("UPDATE pagamentos SET status = 'cancelado' WHERE id = :id"), {'id': pagamento_id})
        conn.commit()
        return {"success": True}

def listar_pagamentos_cliente(cliente_id):
    hoje = date.today().isoformat()
    date_format = get_date_format('p.vencimento')
    with get_engine().connect() as conn:
        result = conn.execute(text(f'''
            SELECT p.*, c.nome as cliente_nome,
                   CASE WHEN p.status = 'pago' THEN 0
                        ELSE {get_date_diff(':hoje', 'p.vencimento')}
                   END as dias_atraso
            FROM pagamentos p
            JOIN clientes c ON p.cliente_id = c.id
            WHERE p.cliente_id = :cliente_id
            ORDER BY p.vencimento DESC
        '''), {'cliente_id': cliente_id, 'hoje': hoje})
        pagamentos = [dict(row._mapping) for row in result]
        return pagamentos

def listar_pagamentos(cliente_id=None, status=None, mes=None):
    """Lista pagamentos com filtros opcionais (compatível com /api/pagamentos GET)."""
    params = {}
    filters = ['1=1']
    if cliente_id:
        filters.append('p.cliente_id = :cliente_id')
        params['cliente_id'] = cliente_id
    if status:
        filters.append('p.status = :status')
        params['status'] = status
    if mes:
        df = get_date_format('p.vencimento')
        filters.append(f"{df} = :mes")
        params['mes'] = mes

    sql = text(f'''
        SELECT p.*, c.nome as cliente_nome
        FROM pagamentos p
        LEFT JOIN clientes c ON p.cliente_id = c.id
        WHERE {' AND '.join(filters)}
        ORDER BY p.vencimento DESC
    ''')
    with get_engine().connect() as conn:
        result = conn.execute(sql, params)
        pagamentos = [dict(row._mapping) for row in result]
        return pagamentos

def atualizar_pagamento(pagamento_id, dados):
    with get_engine().connect() as conn:
        set_clause = ', '.join(f"{k} = :{k}" for k in dados)
        sql = text(f'UPDATE pagamentos SET {set_clause} WHERE id = :id')
        params = {**dados, 'id': pagamento_id}
        conn.execute(sql, params)
        conn.commit()
        return {"success": True}

def deletar_pagamento(pagamento_id):
    with get_engine().connect() as conn:
        conn.execute(text('DELETE FROM pagamentos WHERE id = :id'), {'id': pagamento_id})
        conn.commit()
        return {"success": True}

def obter_estatisticas():
    hoje = date.today().isoformat()
    mes_atual = date.today().strftime('%Y-%m')
    # Para receita do mês, usa data_pagamento quando status = 'pago'
    # Para receita do mês, usa data_pagamento quando status = 'pago'
    date_format_pagamento = get_date_format('p.data_pagamento')
    with get_engine().connect() as conn:
        # Calcula métricas usadas pelo frontend: total_clientes, pagamentos_pendentes, pagamentos_vencidos, valor_recebido_mes
        sql = text(f'''
            SELECT
                COUNT(DISTINCT c.id) as total_clientes,
                SUM(CASE WHEN p.status = 'pendente' THEN 1 ELSE 0 END) as pagamentos_pendentes,
                SUM(CASE WHEN p.status = 'pendente' AND p.vencimento < :hoje THEN 1 ELSE 0 END) as pagamentos_vencidos,
                SUM(CASE WHEN p.status = 'pago' AND {date_format_pagamento} = :mes_atual THEN p.valor ELSE 0 END) as valor_recebido_mes
            FROM clientes c
            LEFT JOIN pagamentos p ON c.id = p.cliente_id
            WHERE c.ativo = TRUE
        ''')
        result = conn.execute(sql, {'hoje': hoje, 'mes_atual': mes_atual})
        stats = dict(result.fetchone()._mapping)
        # Garantir tipos numéricos simples para frontend
        stats['total_clientes'] = int(stats.get('total_clientes') or 0)
        stats['pagamentos_pendentes'] = int(stats.get('pagamentos_pendentes') or 0)
        stats['pagamentos_vencidos'] = int(stats.get('pagamentos_vencidos') or 0)
        stats['valor_recebido_mes'] = float(stats.get('valor_recebido_mes') or 0.0)
        return stats

def obter_inadimplentes():
    hoje = date.today().isoformat()
    with get_engine().connect() as conn:
        result = conn.execute(text(f'''
            SELECT c.id, c.nome, c.telefone, c.email,
                   COUNT(p.id) AS qtd_pendencias,
                   MIN(p.vencimento) as vencimento_mais_antigo,
                   {get_date_diff(':hoje', 'MIN(p.vencimento)')} as dias_atraso,
                   SUM(p.valor) as valor_total
            FROM clientes c
            JOIN pagamentos p ON c.id = p.cliente_id
            WHERE p.status = 'pendente' AND p.vencimento < :hoje AND c.ativo = TRUE
            GROUP BY c.id, c.nome, c.telefone, c.email
            ORDER BY dias_atraso DESC
        '''), {'hoje': hoje})
        inadimplentes = [dict(row._mapping) for row in result]
        # Normaliza tipos
        for r in inadimplentes:
            r['qtd_pendencias'] = int(r.get('qtd_pendencias') or 0)
            r['valor_total'] = float(r.get('valor_total') or 0.0)
        return inadimplentes

def obter_historico_pagamentos(cliente_id):
    """Retorna histórico de pagamentos de um cliente (lista de pagamentos)."""
    with get_engine().connect() as conn:
        result = conn.execute(text('SELECT * FROM pagamentos WHERE cliente_id = :id ORDER BY vencimento DESC'), {'id': cliente_id})
        return [dict(row._mapping) for row in result]

def obter_clientes_pagaram_mes():
    """Retorna clientes que efetuaram pagamento no mês atual."""
    mes_atual = date.today().strftime('%Y-%m')
    df = get_date_format('p.data_pagamento')
    with get_engine().connect() as conn:
        result = conn.execute(text(f'''
            SELECT c.id, c.nome, c.telefone,
                   COUNT(p.id) AS qtd_pagamentos,
                   SUM(p.valor) AS valor_total,
                   MAX(p.data_pagamento) AS ultimo_pagamento
            FROM clientes c
            JOIN pagamentos p ON p.cliente_id = c.id
            WHERE p.status = 'pago' AND {df} = :mes
            GROUP BY c.id, c.nome, c.telefone
            ORDER BY valor_total DESC
        '''), {'mes': mes_atual})
        rows = [dict(row._mapping) for row in result]
        for r in rows:
            r['qtd_pagamentos'] = int(r.get('qtd_pagamentos') or 0)
            r['valor_total'] = float(r.get('valor_total') or 0.0)
            # ultimo_pagamento pode ser None ou string; padroniza para 'YYYY-MM-DD' ou None
            r['ultimo_pagamento'] = r.get('ultimo_pagamento')
        return rows

def obter_relatorio_mensal(mes):
    date_format = get_date_format('p.vencimento')
    with get_engine().connect() as conn:
        result = conn.execute(text(f'''
            SELECT 
                SUM(CASE WHEN status = 'pago' THEN valor ELSE 0 END) as total_pago,
                SUM(CASE WHEN status = 'pendente' THEN valor ELSE 0 END) as total_pendente,
                COUNT(*) as total_pagamentos,
                COUNT(DISTINCT cliente_id) as clientes_ativos
            FROM pagamentos
            WHERE {date_format} = :mes
        '''), {'mes': mes})
        relatorio = dict(result.fetchone()._mapping)
        return relatorio

def buscar_clientes(termo):
    return listar_clientes(termo)  # Reusa listar_clientes com busca