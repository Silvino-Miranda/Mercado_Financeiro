# 🔄 Migração para UV - ML v2

## ✅ Mudanças Realizadas

### 1. **pyproject.toml** (Raiz do Projeto)
Adicionadas dependências de teste:
```toml
dependencies = [
    ...
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]
```

### 2. **setup.ps1** Atualizado
- ✅ Verifica UV em vez de Python genérico
- ✅ Instala pytest apenas se necessário
- ✅ Usa `uv run pytest` para testes
- ✅ Referencia `pyproject.toml` em vez de `requirements.txt`

### 3. **requirements.txt** Removido
❌ Arquivo deletado (não necessário com UV)

### 4. **Documentação Atualizada**
Todos os comandos agora usam `uv run`:
- ✅ README.md
- ✅ QUICK_REFERENCE.md
- ✅ IMPLEMENTATION_SUMMARY.md
- ✅ TROUBLESHOOTING.md (próximo)

---

## 🚀 Como Usar Agora

### Setup Inicial
```powershell
# Opção 1: Script automatizado
./src/ml_v2/setup.ps1

# Opção 2: Manual
uv sync  # Instala todas as deps do pyproject.toml
uv run pytest src/ml_v2/tests/ -v
```

### Executar Pipeline
```bash
# Todos os comandos agora usam 'uv run'
uv run python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv
uv run python src/ml_v2/cli.py evaluate --csv data/BTCUSDT_30m_full.csv
uv run python src/ml_v2/cli.py walkforward --csv data/BTCUSDT_30m_full.csv --folds 3
uv run python src/ml_v2/cli.py backtest --csv data/BTCUSDT_30m_full.csv --start 2024-01-01
```

### Alternativa (com .venv ativado)
```bash
# Se preferir ativar o ambiente:
.\.venv\Scripts\Activate.ps1

# Depois pode usar Python direto
python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv
```

---

## ✅ Testes Validados

```powershell
PS> uv run pytest src/ml_v2/tests/test_no_leak.py -v
=============================================== test session starts ===============================================
platform win32 -- Python 3.12.9, pytest-8.4.2, pluggy-1.6.0
collected 5 items

src\ml_v2\tests\test_no_leak.py::test_scaler_fit_only_on_train PASSED                        [ 20%]
src\ml_v2\tests\test_no_leak.py::test_transform_before_fit_raises_error PASSED               [ 40%]
src\ml_v2\tests\test_no_leak.py::test_inverse_target_returns_correct_scale PASSED            [ 60%]
src\ml_v2\tests\test_no_leak.py::test_sequences_have_correct_shape PASSED                    [ 80%]
src\ml_v2\tests\test_no_leak.py::test_no_data_leakage_in_split PASSED                        [100%]

================================================ 5 passed in 3.28s ================================================
```

---

## 📊 Vantagens do UV

1. **✅ Mais Rápido:** 10-100x mais rápido que pip
2. **✅ Centralizado:** Todas as deps no `pyproject.toml`
3. **✅ Reprodutível:** `uv.lock` garante versões exatas
4. **✅ Isolado:** `.venv` gerenciado automaticamente
5. **✅ Consistente:** Um único gerenciador para todo o projeto

---

## 🔧 Estrutura Final

```
RN_Operar_Cripto/
├── pyproject.toml              ← Deps centralizadas (inclui pytest)
├── uv.lock                     ← Lock file do UV
├── .venv/                      ← Ambiente virtual
│
└── src/
    └── ml_v2/
        ├── cli.py              ← Executar com 'uv run python'
        ├── setup.ps1           ← Usa UV
        ├── tests/              ← Rodar com 'uv run pytest'
        └── [outros arquivos]
```

---

## 🎯 Checklist de Migração

- [x] Adicionar pytest ao pyproject.toml
- [x] Atualizar setup.ps1 para UV
- [x] Remover requirements.txt
- [x] Atualizar README.md
- [x] Atualizar QUICK_REFERENCE.md
- [x] Atualizar IMPLEMENTATION_SUMMARY.md
- [x] Sincronizar deps: `uv sync`
- [x] Validar testes: 5/5 passando ✅

---

## 💡 Próximos Passos

1. **Executar pipeline completo:**
   ```bash
   uv run python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv
   ```

2. **Se necessário, adicionar mais deps:**
   ```bash
   # Editar pyproject.toml, depois:
   uv sync
   ```

3. **Manter documentação atualizada:**
   - Sempre usar `uv run` nos exemplos
   - Referenciar `pyproject.toml` como fonte das deps

---

**Status:** ✅ Migração completa e testada  
**Data:** 16/10/2025  
**Compatibilidade:** UV 0.5+ | Python 3.12+
