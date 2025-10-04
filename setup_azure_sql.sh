#!/bin/bash

# Script de configuração para Azure SQL Database no macOS
# Execute: chmod +x setup_azure_sql.sh && ./setup_azure_sql.sh

echo "🚀 Configurando ambiente para Azure SQL Database no macOS..."

# Verificar se Homebrew está instalado
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew não encontrado. Instalando..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Instalar Azure CLI
echo "📦 Instalando Azure CLI..."
brew install azure-cli

# Instalar Azure Data Studio
echo "📦 Instalando Azure Data Studio..."
brew install --cask azure-data-studio

# Instalar Microsoft ODBC Driver
echo "📦 Instalando Microsoft ODBC Driver..."
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18

# Instalar Python e dependências
echo "🐍 Configurando Python e dependências..."
if ! command -v python3 &> /dev/null; then
    brew install python3
fi

# Instalar dependências Python
pip3 install -r requirements.txt

# Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."
echo 'export PATH="$PATH:/opt/homebrew/bin"' >> ~/.zshrc
echo 'export PATH="$PATH:/opt/homebrew/opt/mssql-tools18/bin"' >> ~/.zshrc

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "⚠️  Configure suas credenciais no arquivo .env"
fi

echo "✅ Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas credenciais no arquivo .env"
echo "2. Execute: python3 azure_sql_connector.py"
echo "3. Ou abra o Azure Data Studio para interface gráfica"
echo ""
echo "🔧 Comandos úteis:"
echo "- az login (para autenticar no Azure)"
echo "- az sql server list (listar servidores SQL)"
echo "- sqlcmd -S seu-servidor.database.windows.net -d seu-banco -U seu-usuario -P sua-senha"