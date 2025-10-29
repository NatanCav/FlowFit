import sqlite3
import os
from werkzeug.security import generate_password_hash

# Caminho para o arquivo do banco de dados
DB_PATH = os.path.join('data', 'database.db')

def init_db():
   
    # Cria a pasta 'data' se não existir
    os.makedirs('data', exist_ok=True)
    
    conn = None  # CORREÇÃO: Inicializa variável antes do try
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # ============================================
        # Tabela de Usuários (para login no sistema)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo TEXT DEFAULT 'operador',  -- Tipos: 'admin' ou 'operador'
                ativo BOOLEAN DEFAULT 1,  -- 1=ativo, 0=inativo
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso TIMESTAMP
            )
        ''')
        
        # ============================================
        # Tabela de Clientes/Alunos
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT,  -- Email pode ser opcional
                telefone TEXT,
                cpf TEXT UNIQUE,  -- CPF único para identificação
                endereco TEXT,
                observacoes TEXT,  -- Notas sobre o cliente (restrições, preferências, etc)
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1  -- 1=ativo, 0=inativo
            )
        ''')
        
        # ============================================
        # Tabela de Pagamentos
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                valor REAL NOT NULL,  -- Valor do pagamento em R$
                vencimento DATE NOT NULL,  -- Data de vencimento
                data_pagamento DATE,  -- Data em que foi pago (NULL se ainda não pago)
                status TEXT DEFAULT 'pendente',  -- Status: 'pendente', 'pago', 'atrasado', 'cancelado'
                descricao TEXT,  -- Descrição do pagamento (ex: "Mensalidade Janeiro 2025")
                metodo_pagamento TEXT,  -- Forma de pagamento: 'dinheiro', 'pix', 'cartão', etc
                observacoes TEXT,  -- Observações adicionais
                usuario_registro_id INTEGER,  -- Usuário que registrou o pagamento
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Define a relação com a tabela clientes
                FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
                -- Define a relação com a tabela usuarios
                FOREIGN KEY (usuario_registro_id) REFERENCES usuarios (id)
            )
        ''')
        
        # ============================================
        # Tabela de Histórico de Ações (auditoria)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                acao TEXT NOT NULL,  -- Descrição da ação realizada
                descricao TEXT,  -- Detalhes adicionais da ação
                data_acao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Define a relação com a tabela usuarios
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # ============================================
        # Índices para melhorar performance nas consultas
        # ============================================
        # Índice para buscar pagamentos por cliente
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cliente_id ON pagamentos(cliente_id)')
        
        # Índice para buscar pagamentos por status
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON pagamentos(status)')
        
        # Índice para buscar pagamentos por vencimento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vencimento ON pagamentos(vencimento)')
        
        # Índice para buscar usuários por email (usado no login)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuarios(email)')
        
        # ============================================
        # Cria usuário administrador padrão
        # ============================================
        # Verifica se já existe algum usuário administrador
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE email = ?', ('admin@sistema.com',))
        if cursor.fetchone()[0] == 0:
            # Gera hash seguro da senha padrão
            senha_hash = generate_password_hash('admin123')
            
            # Insere o usuário administrador
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha_hash, tipo)
                VALUES (?, ?, ?, ?)
            ''', ('Administrador', 'admin@sistema.com', senha_hash, 'admin'))
            
            print("   Email: admin@sistema.com")
            print("   Senha: admin123")
        
        # Salva as alterações no banco de dados
        conn.commit()
        print("✓ Banco de dados inicializado com sucesso!")
        
    except sqlite3.Error as e:
        print(f"✗ Erro ao inicializar banco de dados: {e}")
        if conn:
            conn.rollback()  # Desfaz alterações em caso de erro
        raise  # Re-lança a exceção para tratamento superior
    finally:
        if conn:  # CORREÇÃO: Verifica se conn existe antes de fechar
            conn.close()


def get_connection():
    """

    Returns:
        sqlite3.Connection: Objeto de conexão com o banco de dados
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        # row_factory permite acessar colunas por nome: row['nome'] ao invés de row[0]
        # Isso DEVE ser definido após connect() mas ANTES de usar o cursor
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"✗ Erro ao conectar ao banco de dados: {e}")
        raise  # Re-lança a exceção para ser tratada pelo código chamador