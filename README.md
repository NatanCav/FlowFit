# 💰 Sistema de Gerenciamento de Pagamentos

Sistema completo desenvolvido para auxiliar academias, escolas e pequenos negócios no gerenciamento de pagamentos de clientes/alunos e controle de inadimplência.

## 🚀 Tecnologias Utilizadas

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python 3.8+ com Flask
- **Banco de Dados:** SQLite3
- **Autenticação:** JWT (JSON Web Tokens)

## 📁 Estrutura do Projeto

```
payment-manager/
│
├── backend/
│   ├── __init__.py          # Inicializador do pacote
│   ├── app.py               # Servidor Flask e rotas da API
│   ├── database.py          # Configuração e inicialização do banco
│   ├── models.py            # Modelos e operações de dados
│   └── auth.py              # Sistema de autenticação
│
├── frontend/
│   ├── login.html           # Página de login
│   ├── dashboard.html       # Painel principal
│   ├── clientes.html        # Lista de clientes
│   ├── cadastro-cliente.html    # Cadastro de novo cliente
│   ├── editar-cliente.html      # Edição de cliente
│   ├── inadimplentes.html       # Lista de inadimplentes
│   ├── usuarios.html            # Gerenciamento de usuários (admin)
│   ├── historico-pagamento.html # Histórico de pagamentos
│   │
│   ├── css/
│   │   ├── style.css        # Estilos principais
│   │   └── login.css        # Estilos da página de login
│   │
│   └── js/
│       ├── auth.js          # Controle de autenticação
│       └── utils.js         # Funções utilitárias
│
├── data/
│   └── database.db          # Banco de dados (gerado automaticamente)
│
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

## 📋 Funcionalidades

### 🔐 Sistema de Autenticação
- Login com email e senha
- Controle de sessão com JWT
- Dois níveis de acesso: Administrador e Operador

### 👥 Gerenciamento de Clientes
- Cadastro completo de clientes
- Edição de dados cadastrais
- Busca por nome ou CPF
- Visualização de histórico

### 💳 Controle de Pagamentos
- Cadastro de pagamentos com vencimento
- Registro de recebimentos
- Múltiplos métodos de pagamento
- Histórico completo por cliente

### 📊 Dashboard e Relatórios
- Estatísticas em tempo real
- Lista de inadimplentes
- Clientes que pagaram no mês
- Alertas de pagamentos vencidos

### 👤 Gerenciamento de Usuários (Admin)
- Criação de novos usuários
- Definição de permissões
- Histórico de ações no sistema

## 🔧 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Navegador web moderno (Chrome, Firefox, Edge)

### Passo 1: Clone ou baixe o projeto

```bash
# Se estiver usando git
git clone <url-do-repositorio>
cd payment-manager

# Ou simplesmente extraia o arquivo ZIP
```

### Passo 2: Instale as dependências

```bash
pip install -r requirements.txt
```

### Passo 3: Inicie o servidor backend

```bash
# Navegue até a pasta backend
cd backend

# Inicie o servidor
python app.py
```

Você verá uma mensagem assim:
```
==================================================
🚀 SISTEMA DE GERENCIAMENTO DE PAGAMENTOS
==================================================
📊 Frontend: Abra o arquivo frontend/login.html no navegador
🔌 API: http://localhost:5000/api
==================================================
👤 Usuário padrão:
   Email: admin@sistema.com
   Senha: admin123
==================================================
```

### Passo 5: Abra o frontend

1. Mantenha o servidor backend rodando
2. Abra o arquivo `frontend/login.html` no seu navegador
3. Faça login com as credenciais padrão:
   - **Email:** admin@sistema.com
   - **Senha:** admin123

## 🎯 Como Usar

### Primeiro Acesso

1. **Login:** Use as credenciais padrão (admin@sistema.com / admin123)
2. **Dashboard:** Visualize as estatísticas gerais do sistema
3. **Cadastre clientes:** Vá em "Clientes" → "Novo Cliente"
4. **Adicione pagamentos:** Acesse o histórico de um cliente e adicione pagamentos

### Fluxo de Trabalho Recomendado

1. **Cadastrar Clientes**
   - Menu: Clientes → Novo Cliente
   - Preencha os dados (nome obrigatório, demais opcionais)

2. **Registrar Pagamentos**
   - Acesse o histórico do cliente
   - Clique em "Novo Pagamento"
   - Defina valor e data de vencimento

3. **Registrar Recebimentos**
   - No histórico do cliente, clique no ✓ verde
   - Selecione o método de pagamento
   - O sistema registra a data atual automaticamente

4. **Monitorar Inadimplentes**
   - Menu: Inadimplentes
   - Veja lista completa com dias de atraso
   - Clique em "Ver Detalhes" para mais informações

5. **Gerenciar Usuários** (Apenas Admin)
   - Menu: Usuários
   - Crie operadores para sua equipe
   - Admins têm acesso total, operadores gerenciam apenas clientes e pagamentos

## 🔑 Tipos de Usuário

### Administrador
- Acesso total ao sistema
- Gerencia usuários
- Visualiza histórico de ações
- Todas as funções de operador

### Operador
- Gerencia clientes
- Controla pagamentos
- Visualiza relatórios
- Não pode criar/editar usuários

## 🎨 Personalização

### Alterar Cores
Edite o arquivo `frontend/css/style.css` na seção de variáveis:

```css
:root {
    --primary: #4f46e5;      /* Cor principal */
    --success: #10b981;      /* Verde (sucesso) */
    --danger: #ef4444;       /* Vermelho (erro) */
    --warning: #f59e0b;      /* Laranja (alerta) */
}
```

### Alterar Porta do Servidor
Edite `backend/app.py` na última linha:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Altere 5000 para sua porta
```

**IMPORTANTE:** Se alterar a porta, atualize também em `frontend/js/utils.js`:

```javascript
const API_URL = 'http://localhost:5000/api';  // Atualize a porta aqui
```

## 🔒 Segurança

### Produção
Se for usar em produção, altere:

1. **Chave Secreta do JWT** em `backend/auth.py`:
```python
SECRET_KEY = 'sua-chave-secreta-aqui-mude-em-producao'  # Altere esta linha!
```

2. **Debug Mode** em `backend/app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)  # debug=False em produção
```

3. **Altere a senha do admin** após primeiro login

## 🐛 Solução de Problemas

### Erro: "Módulo não encontrado"
```bash
pip install -r requirements.txt
```

### Erro: "Erro ao conectar com o servidor"
- Verifique se o backend está rodando
- Confirme se a porta 5000 está disponível
- Verifique o console do navegador (F12) para erros

### Erro: "Token expirado"
- Faça logout e login novamente
- Tokens expiram após 8 horas

### Banco de dados corrompido
Delete o arquivo `data/database.db` e reinicie o servidor. Um novo banco será criado automaticamente.

## 📝 Licença

Este projeto é de código aberto e pode ser usado livremente para fins educacionais e comerciais.

## 👨‍💻 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de Solução de Problemas
2. Consulte os comentários no código
3. Abra uma issue no repositório

## 🎉 Pronto!

Seu sistema está funcionando! Explore todas as funcionalidades e personalize conforme necessário.

**Dica:** Crie um usuário operador de teste para sua equipe e mantenha o admin apenas para você.