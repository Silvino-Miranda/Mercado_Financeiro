# 🚀 Guia Rápido - UV

## 📋 Comandos Essenciais

### 🔧 Instalação Inicial
```powershell
# Instalar UV (apenas uma vez)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Configurar projeto (executar no diretório do projeto)
uv sync
```

### 📦 Gerenciamento de Pacotes
```powershell
# Adicionar novo pacote
uv add nome-do-pacote

# Adicionar pacote de desenvolvimento
uv add --dev nome-do-pacote

# Remover pacote
uv remove nome-do-pacote

# Atualizar todas as dependências
uv lock --upgrade

# Atualizar pacote específico
uv lock --upgrade-package nome-do-pacote

# Sincronizar ambiente (instalar/atualizar conforme pyproject.toml)
uv sync

# Reinstalar tudo do zero
uv sync --reinstall
```

### 🐍 Executando Python
```powershell
# Executar script com uv (não precisa ativar ambiente)
uv run python script.py
uv run python src/ml/main_train.py
uv run python src/run_webapp.py

# Executar comando Python direto
uv run python -c "import pandas; print(pandas.__version__)"

# Ativar ambiente manualmente (se preferir)
.\.venv\Scripts\Activate.ps1  # PowerShell
.\activate.bat                 # CMD
```

### 🔍 Informações
```powershell
# Versão do UV
uv --version

# Listar pacotes instalados
uv pip list

# Mostrar informações de um pacote
uv pip show nome-do-pacote

# Verificar ambiente Python
uv python list
```

### 🛠️ Manutenção
```powershell
# Limpar cache do UV
uv cache clean

# Verificar integridade das dependências
uv sync --check

# Exportar para requirements.txt (compatibilidade)
uv pip freeze > requirements.txt
```

## 🎯 Workflows Comuns

### Novo Desenvolvedor Clonando o Projeto
```powershell
# 1. Clonar repositório
git clone <url>
cd RN_Operar_Cripto

# 2. Instalar UV (se necessário)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Configurar ambiente
uv sync

# 4. Pronto! Executar
uv run python src/run_webapp.py
```

### Adicionar Nova Dependência
```powershell
# 1. Adicionar pacote
uv add requests

# 2. O pyproject.toml é atualizado automaticamente
# 3. O uv.lock é atualizado automaticamente
# 4. Comitar mudanças
git add pyproject.toml uv.lock
git commit -m "Add requests dependency"
```

### Atualizar Dependências
```powershell
# 1. Atualizar todas
uv lock --upgrade
uv sync

# 2. Testar aplicação
uv run python -m pytest

# 3. Se OK, comitar
git add uv.lock
git commit -m "Update dependencies"
```

### Resolver Problemas
```powershell
# Ambiente corrompido? Reinstalar tudo
Remove-Item -Recurse -Force .venv
uv sync --reinstall

# Dependências conflitantes? Ver detalhes
uv sync --verbose

# Cache com problemas? Limpar
uv cache clean
uv sync
```

## 📱 Scripts de Atalho

### Treinar Modelo
```powershell
uv run python src/ml/main_train.py
```

### Fazer Predições
```powershell
uv run python src/ml/main_predict.py
```

### Executar Dashboard
```powershell
uv run python src/run_webapp.py
```

### Preparar Dados
```powershell
uv run python src/prepare_data.py
```

### Executar Backtesting
```powershell
uv run python src/ml/backtesting/backtester.py
```

## 🔥 Dicas Pro

### Executar múltiplos comandos
```powershell
uv run python -c "
import pandas as pd
import tensorflow as tf
print(f'Pandas: {pd.__version__}')
print(f'TensorFlow: {tf.__version__}')
"
```

### Instalar wheel local (TA-Lib)
```powershell
uv pip install _Arquivos/TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
```

### Criar ambiente em local diferente
```powershell
uv venv --python 3.12 meu-ambiente
```

### Usar versão específica de Python
```powershell
uv venv --python 3.11
```

## 📊 Comparação com pip

| Tarefa | pip | uv |
|--------|-----|-----|
| Instalar deps | `pip install -r requirements.txt` | `uv sync` |
| Adicionar pacote | Editar requirements.txt + `pip install` | `uv add pacote` |
| Remover pacote | Editar requirements.txt + `pip uninstall` | `uv remove pacote` |
| Executar | `python script.py` | `uv run python script.py` |
| Velocidade | 🐌 Lento | ⚡ Muito rápido |

## 🆘 Ajuda

```powershell
# Ajuda geral
uv --help

# Ajuda de comando específico
uv sync --help
uv add --help
uv run --help
```

## 🔗 Links Úteis

- [Documentação Oficial](https://docs.astral.sh/uv/)
- [GitHub do UV](https://github.com/astral-sh/uv)
- [MIGRATION_UV.md](MIGRATION_UV.md) - Guia completo de migração
