# Azure SQL Database - MacBook Setup

Este repositório contém scripts e ferramentas para conectar e fazer queries no Azure SQL Database usando um MacBook.

## 🚀 Configuração Rápida

### 1. Executar Script de Configuração
```bash
./setup_azure_sql.sh
```

### 2. Configurar Credenciais
Edite o arquivo `.env` com suas credenciais:
```bash
cp .env.example .env
nano .env
```

## 🛠️ Ferramentas Disponíveis

### 1. Azure Data Studio (Recomendado)
- Interface gráfica moderna
- Suporte nativo ao Azure SQL
- IntelliSense e notebooks integrados
- **Instalação**: `brew install --cask azure-data-studio`

### 2. Python Scripts
- `azure_sql_connector.py`: Classe para conectar e executar queries
- `azure_sql_queries.py`: Queries úteis para análise e manutenção

### 3. Azure CLI + SQLCMD
- `az login`: Autenticar no Azure
- `sqlcmd`: Executar queries via terminal

## 📋 Exemplos de Uso

### Python - Conexão Básica
```python
from azure_sql_connector import AzureSQLConnector

# Configurar conexão
sql_conn = AzureSQLConnector(
    server="seu-servidor.database.windows.net",
    database="seu-banco",
    username="seu-usuario",
    password="sua-senha"
)

# Conectar e executar query
if sql_conn.connect():
    result = sql_conn.execute_query("SELECT TOP 10 * FROM sua_tabela")
    print(result)
    sql_conn.close()
```

### Python - Queries de Análise
```python
from azure_sql_queries import AzureSQLQueries

queries = AzureSQLQueries(sql_conn)

# Tamanho das tabelas
table_sizes = queries.get_table_sizes()

# Fragmentação dos índices
fragmentation = queries.get_index_fragmentation()

# Executar manutenção
queries.run_maintenance_script()
```

### Terminal - SQLCMD
```bash
sqlcmd -S seu-servidor.database.windows.net \
       -d seu-banco \
       -U seu-usuario \
       -P sua-senha \
       -Q "SELECT TOP 10 * FROM sua_tabela"
```

## 🔧 Queries Úteis Incluídas

- **Informações do Banco**: Versão, usuário atual, data/hora
- **Tamanhos das Tabelas**: Espaço usado, não usado, contagem de linhas
- **Fragmentação de Índices**: Análise e recomendações
- **Queries Lentas**: Performance (requer Query Store)
- **Conexões Ativas**: Monitoramento de sessões
- **Sessões Bloqueadas**: Identificação de bloqueios
- **Script de Manutenção**: Execução do AzureSQLMaintenance

## 📦 Dependências

- Python 3.7+
- pyodbc
- pandas
- python-dotenv
- Azure CLI
- Microsoft ODBC Driver 18
- Azure Data Studio

## 🔐 Segurança

- Use variáveis de ambiente para credenciais
- Nunca commite senhas no código
- Use autenticação Azure AD quando possível
- Configure firewall do Azure SQL adequadamente

## 📚 Recursos Adicionais

- [Documentação Azure SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/)
- [Azure Data Studio](https://docs.microsoft.com/en-us/sql/azure-data-studio/)
- [ODBC Driver para SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/)