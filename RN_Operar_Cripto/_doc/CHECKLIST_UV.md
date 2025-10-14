# ✅ Lista de Verificação - Migração UV

Use esta checklist para verificar se a migração foi concluída com sucesso.

## 📋 Verificação de Arquivos

### ✅ Arquivos que DEVEM existir:
- [ ] `pyproject.toml` - Configuração principal
- [ ] `.python-version` - Versão do Python (3.12)
- [ ] `setup.ps1` - Script de instalação PowerShell
- [ ] `setup.bat` - Script de instalação CMD
- [ ] `activate.bat` - Script de ativação
- [ ] `.gitignore` - Atualizado para UV
- [ ] `MIGRATION_UV.md` - Documentação completa
- [ ] `UV_QUICK_GUIDE.md` - Guia rápido
- [ ] `CHANGELOG_UV.md` - Registro de mudanças
- [ ] `CLEANUP_SUMMARY.md` - Resumo da limpeza

### ❌ Arquivos que NÃO devem existir:
- [ ] ~~`requirements.in`~~ - REMOVIDO ✅
- [ ] ~~`requirements.txt`~~ - REMOVIDO ✅
- [ ] ~~`uv.lock`~~ (placeholder) - REMOVIDO ✅ (será gerado pelo uv sync)

## 🧪 Testes de Funcionalidade

### 1. Verificar Instalação do UV
```powershell
uv --version
```
**Resultado esperado:** Versão do UV (ex: `uv 0.x.x`)

### 2. Sincronizar Ambiente
```powershell
uv sync
```
**Resultado esperado:** 
- Criação da pasta `.venv`
- Instalação de ~70 pacotes
- Geração do arquivo `uv.lock`
- Sem erros

### 3. Verificar Python
```powershell
uv run python --version
```
**Resultado esperado:** `Python 3.12.x`

### 4. Verificar Dependências Principais
```powershell
uv run python -c "import tensorflow; print(f'TensorFlow: {tensorflow.__version__}')"
uv run python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
uv run python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
uv run python -c "import dash; print(f'Dash: {dash.__version__}')"
```
**Resultado esperado:** Versões dos pacotes sem erros

### 5. Testar Backtesting
```powershell
uv run python -c "import backtrader; print(f'Backtrader: {backtrader.__version__}')"
```
**Resultado esperado:** Versão do Backtrader

### 6. Verificar Estrutura de Pacotes
```powershell
uv pip list | Select-String -Pattern "tensorflow|pandas|numpy|dash|keras"
```
**Resultado esperado:** Lista com os pacotes principais instalados

### 7. Testar Script de Preparação de Dados
```powershell
uv run python src/prepare_data.py
```
**Resultado esperado:** Execução sem erros

## 📊 Verificação de Performance

### Tempo de Instalação (primeira vez)
```powershell
Measure-Command { uv sync }
```
**Resultado esperado:** ~30-90 segundos

### Tempo de Sincronização (com cache)
```powershell
# Após primeira instalação
Measure-Command { uv sync }
```
**Resultado esperado:** ~5-15 segundos

## 🔍 Verificação do Git

### Verificar Status
```powershell
git status
```

### Arquivos que DEVEM aparecer como modificados/novos:
- [x] `pyproject.toml` (novo)
- [x] `.python-version` (novo)
- [x] `.gitignore` (modificado)
- [x] `README.md` (modificado)
- [x] `setup.ps1` (novo)
- [x] `setup.bat` (novo)
- [x] `MIGRATION_UV.md` (novo)
- [x] `UV_QUICK_GUIDE.md` (novo)
- [x] `CHANGELOG_UV.md` (novo)
- [x] `CLEANUP_SUMMARY.md` (novo)

### Arquivos que DEVEM aparecer como deletados:
- [x] `requirements.in` (deletado)
- [x] `requirements.txt` (deletado)

## 🎯 Testes de Integração

### 1. Treinar Modelo (teste básico)
```powershell
# Apenas verificar se o script inicia sem erros de importação
uv run python -c "from src.ml.main_train import *; print('✅ Imports OK')"
```

### 2. Webapp (teste básico)
```powershell
# Verificar imports do webapp
uv run python -c "from src.webapp.app import *; print('✅ Webapp imports OK')"
```

### 3. Indicadores Técnicos
```powershell
uv run python -c "from src.ml.data.indicator import *; print('✅ Indicators OK')"
```

## 📝 Checklist Final

### Ambiente:
- [ ] UV instalado e funcionando
- [ ] `uv sync` executado com sucesso
- [ ] `.venv` criado
- [ ] `uv.lock` gerado
- [ ] Python 3.12 ativo no ambiente

### Dependências:
- [ ] TensorFlow instalado
- [ ] Pandas instalado
- [ ] NumPy instalado
- [ ] Keras instalado
- [ ] Dash instalado
- [ ] Backtrader instalado
- [ ] Todas as ~70 dependências instaladas

### Documentação:
- [ ] README.md atualizado
- [ ] MIGRATION_UV.md criado
- [ ] UV_QUICK_GUIDE.md criado
- [ ] CHANGELOG_UV.md criado
- [ ] CLEANUP_SUMMARY.md criado

### Scripts:
- [ ] `setup.ps1` funcional
- [ ] `setup.bat` funcional
- [ ] `activate.bat` funcional

### Git:
- [ ] Arquivos antigos removidos
- [ ] Novos arquivos criados
- [ ] `.gitignore` atualizado
- [ ] Pronto para commit

## 🚀 Comandos de Teste Rápido

Copie e cole este bloco para testar tudo de uma vez:

```powershell
Write-Host "`n🔍 TESTE 1: Verificando UV..." -ForegroundColor Cyan
uv --version

Write-Host "`n🔍 TESTE 2: Verificando Python..." -ForegroundColor Cyan
uv run python --version

Write-Host "`n🔍 TESTE 3: Verificando TensorFlow..." -ForegroundColor Cyan
uv run python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"

Write-Host "`n🔍 TESTE 4: Verificando Pandas..." -ForegroundColor Cyan
uv run python -c "import pandas as pd; print(f'Pandas: {pd.__version__}')"

Write-Host "`n🔍 TESTE 5: Verificando NumPy..." -ForegroundColor Cyan
uv run python -c "import numpy as np; print(f'NumPy: {np.__version__}')"

Write-Host "`n🔍 TESTE 6: Verificando Keras..." -ForegroundColor Cyan
uv run python -c "import keras; print(f'Keras: {keras.__version__}')"

Write-Host "`n🔍 TESTE 7: Verificando Dash..." -ForegroundColor Cyan
uv run python -c "import dash; print(f'Dash: {dash.__version__}')"

Write-Host "`n🔍 TESTE 8: Verificando Backtrader..." -ForegroundColor Cyan
uv run python -c "import backtrader; print(f'Backtrader: {backtrader.__version__}')"

Write-Host "`n✅ TODOS OS TESTES CONCLUÍDOS!" -ForegroundColor Green
```

## ✅ Critérios de Sucesso

A migração é considerada bem-sucedida se:

1. ✅ `uv sync` executa sem erros
2. ✅ Todos os imports principais funcionam
3. ✅ Python 3.12 está ativo
4. ✅ ~70 pacotes instalados
5. ✅ `uv.lock` gerado automaticamente
6. ✅ Scripts de teste executam sem erros de importação
7. ✅ Arquivos antigos (`requirements.*`) foram removidos
8. ✅ Documentação completa criada

## 🆘 Troubleshooting

### Se `uv` não for encontrado:
```powershell
# Reinstalar UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Reiniciar terminal
```

### Se `uv sync` falhar:
```powershell
# Limpar e reinstalar
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
uv cache clean
uv sync --reinstall
```

### Se houver conflitos de dependências:
```powershell
uv sync --verbose
```

---

**Data do Checklist:** 2025-10-14  
**Versão do UV:** Latest  
**Python:** 3.12  
**Status:** ✅ Pronto para testes
