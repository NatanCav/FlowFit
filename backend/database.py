# database.py atualizado
import os
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash
import sqlite3
import pathlib

DB_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/database.db')
engine = create_engine(DB_URL, echo=False)

def init_db():
    try:
        with engine.connect() as conn:
            # Tabela de Usuários
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    tipo TEXT DEFAULT 'operador',
                    ativo BOOLEAN DEFAULT TRUE,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultimo_acesso TIMESTAMP
                )
            '''))

            # Tabela de Clientes
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    email TEXT,
                    telefone TEXT,
                    cpf TEXT UNIQUE,
                    endereco TEXT,
                    observacoes TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT TRUE
                )
            '''))

            # Tabela de Pagamentos
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS pagamentos (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER NOT NULL,
                    valor REAL NOT NULL,
                    vencimento DATE NOT NULL,
                    data_pagamento DATE,
                    status TEXT DEFAULT 'pendente',
                    descricao TEXT,
                    metodo_pagamento TEXT,
                    observacoes TEXT,
                    usuario_registro_id INTEGER,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios (id)
                )
            '''))

            # Tabela de Histórico
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS historico (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    acao TEXT NOT NULL,
                    descricao TEXT,
                    data_acao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            '''))

            # Índices
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_cliente_id ON pagamentos(cliente_id)'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_status ON pagamentos(status)'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_vencimento ON pagamentos(vencimento)'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuarios(email)'))

            # Cria admin padrão
            result = conn.execute(text('SELECT COUNT(*) FROM usuarios WHERE email = :email'), {'email': 'admin@sistema.com'})
            if result.fetchone()[0] == 0:
                senha_hash = generate_password_hash('admin123')
                conn.execute(text('''
                    INSERT INTO usuarios (nome, email, senha_hash, tipo)
                    VALUES (:nome, :email, :senha_hash, :tipo)
                '''), {'nome': 'Administrador', 'email': 'admin@sistema.com', 'senha_hash': senha_hash, 'tipo': 'admin'})
                print("Admin criado: admin@sistema.com / admin123")

            conn.commit()
        print("✓ Banco de dados inicializado!")
    except Exception as e:
        print(f"✗ Erro ao inicializar DB: {e}")
        raise

def get_engine():
    return engine

def get_date_format(field):
    if 'postgres' in DB_URL:
        return f"to_char({field}, 'YYYY-MM')"
    return f"strftime('%Y-%m', {field})"

def get_date_diff(field1, field2):
    if 'postgres' in DB_URL:
        return f"DATE_PART('day', {field1}::timestamp - {field2}::timestamp)"
    return f"JULIANDAY({field1}) - JULIANDAY({field2})"

def get_connection():
    """Retorna uma conexão DB-API compatível com o código que usa sqlite3-style cursors.

    - Se o `DB_URL` aponta para SQLite (contém 'sqlite'), cria/retorna uma
      conexão `sqlite3.Connection` com `row_factory=sqlite3.Row`.
    - Caso contrário, retorna `engine.raw_connection()` (conexão bruta do SQLAlchemy).

    OBS: Para PostgreSQL/otros DBs, o código que usa placeholders '?' pode precisar
    ser adaptado (psycopg2 usa %s). Esta função prioriza compatibilidade local com SQLite.
    """
    # SQLite: extrai o caminho do DB após o prefixo sqlite:/// ou sqlite://
    if 'sqlite' in DB_URL:
        # Suporta formatos: sqlite:///./data/database.db ou sqlite:///absolute/path.db
        path = DB_URL.split('sqlite:///')[-1]
        # Se ainda contiver prefixos como sqlite://, remove
        path = path.lstrip('/') if path.startswith('./') else path

        # Normaliza para caminho absoluto relativo ao diretório do arquivo
        db_path = pathlib.Path(path)
        if not db_path.is_absolute():
            # relativo ao diretório backend/
            base_dir = pathlib.Path(__file__).resolve().parent
            db_path = (base_dir / db_path).resolve()

        # Cria diretório se necessário
        if not db_path.parent.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    # Para outros DBs, devolve a conexão bruta do SQLAlchemy
    try:
        return engine.raw_connection()
    except Exception:
        raise RuntimeError('Não foi possível obter conexão bruta para o DB configurado')