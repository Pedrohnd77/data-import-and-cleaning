#!/bin/bash
# ============================================================
# local_setup.sh — NBA Stats EDA Pipeline
# ============================================================
# Cria e ativa um ambiente virtual isolado para desenvolvimento
# e testes locais do pipeline, sem impactar outros projetos.
#
# Uso:
#   chmod +x local_setup.sh
#   source local_setup.sh          ← use 'source' para ativar o venv na sessão atual
#
# Após o setup, você pode rodar o script diretamente:
#   python dags/scripts/nba_stats_eda.py
# ============================================================

# ----------------------------------------------------------
# 1. Verificar Python 3
# ----------------------------------------------------------
echo "🔍 Verificando Python..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale antes de continuar."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION encontrado."

# ----------------------------------------------------------
# 2. Criar o ambiente virtual (se ainda não existir)
# ----------------------------------------------------------
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "📦 Criando ambiente virtual em ./$VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Ambiente virtual criado."
else
    echo ""
    echo "⚡ Ambiente virtual já existe em ./$VENV_DIR — reutilizando."
fi

# ----------------------------------------------------------
# 3. Ativar o ambiente virtual
# ----------------------------------------------------------
echo ""
echo "🚀 Ativando o ambiente virtual..."
source "$VENV_DIR/bin/activate"
echo "✅ Ambiente virtual ativo: $(which python)"

# ----------------------------------------------------------
# 4. Atualizar pip e instalar dependências
# ----------------------------------------------------------
echo ""
echo "📥 Instalando dependências de requirements.txt ..."
pip install --upgrade pip --quiet
pip install -r requirements.txt

echo ""
echo "✅ Dependências instaladas:"
pip list | grep -E "numpy|pandas|matplotlib"

# ----------------------------------------------------------
# 5. Exportar variáveis de ambiente do pipeline
# ----------------------------------------------------------
echo ""
echo "🔧 Configurando variáveis de ambiente..."

# Caminhos locais (relativo à raiz do projeto)
export NBA_DATA_PATH="$(pwd)/data"
export NBA_OUTPUT_PATH="$(pwd)/outputs"

# Criar pastas se não existirem
mkdir -p "$NBA_DATA_PATH" "$NBA_OUTPUT_PATH"

echo "   NBA_DATA_PATH   = $NBA_DATA_PATH"
echo "   NBA_OUTPUT_PATH = $NBA_OUTPUT_PATH"

# ----------------------------------------------------------
# 6. Verificar se os CSVs estão presentes
# ----------------------------------------------------------
echo ""
echo "📂 Verificando arquivos de dados..."

REGULAR="$NBA_DATA_PATH/2022-2023 NBA Player Stats - Regular.csv"
PLAYOFFS="$NBA_DATA_PATH/2022-2023 NBA Player Stats - Playoffs.csv"

if [ ! -f "$REGULAR" ]; then
    echo "⚠️  AVISO: CSV de temporada regular não encontrado em data/"
    echo "   Baixe em: https://www.kaggle.com/datasets/vivovinco/20222023-nba-player-stats-regular"
else
    echo "✅ Regular season CSV encontrado."
fi

if [ ! -f "$PLAYOFFS" ]; then
    echo "⚠️  AVISO: CSV de playoffs não encontrado em data/"
else
    echo "✅ Playoffs CSV encontrado."
fi

# ----------------------------------------------------------
# 7. Pronto!
# ----------------------------------------------------------
echo ""
echo "=============================================="
echo "✅ Setup concluído! Ambiente pronto para uso."
echo "=============================================="
echo ""
echo "Para rodar o pipeline localmente:"
echo "   python dags/scripts/nba_stats_eda.py"
echo ""
echo "Para desativar o ambiente virtual:"
echo "   deactivate"
echo ""