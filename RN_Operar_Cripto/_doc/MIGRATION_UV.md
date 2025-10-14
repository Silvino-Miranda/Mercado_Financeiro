# Migração para UV - Gerenciador de Pacotes

Este projeto foi migrado para usar o **uv** como gerenciador de pacotes Python.

## 🚀 O que é o UV?

O `uv` é um gerenciador de pacotes Python extremamente rápido, escrito em Rust, que substitui o pip e o pip-tools. É até 100x mais rápido que o pip tradicional.

## 📦 Instalação do UV

### Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Alternativa usando pip
```powershell
pip install uv
```

## 🔧 Comandos Principais

### 1. Criar/Sincronizar ambiente virtual
```powershell
uv sync
```
Este comando irá:
- Criar um ambiente virtual em `.venv` se não existir
- Instalar todas as dependências do `pyproject.toml`
- Gerar/atualizar o `uv.lock`

### 2. Adicionar nova dependência
```powershell
uv add nome-do-pacote
```

### 3. Remover dependência
```powershell
uv remove nome-do-pacote
```

### 4. Atualizar dependências
```powershell
uv lock --upgrade
```

### 5. Executar scripts Python
```powershell
uv run python script.py
```

### 6. Ativar ambiente virtual manualmente
```powershell
.\.venv\Scripts\Activate.ps1
# ou no CMD:
activate.bat
```

## 📋 Estrutura de Arquivos

- **`pyproject.toml`**: Arquivo principal com todas as dependências do projeto
- **`.python-version`**: Define a versão do Python a ser usada (3.12)
- **`uv.lock`**: Arquivo de lock gerado automaticamente pelo uv (será criado no primeiro `uv sync`)
- **`setup.ps1`** e **`setup.bat`**: Scripts de instalação automatizada

## 🔄 Migrando do pip-tools para uv

### ✅ Arquivos Removidos:
- ~~`requirements.in`~~ → Substituído por `pyproject.toml`
- ~~`requirements.txt`~~ → Substituído por `pyproject.toml` + `uv.lock`

### Antes (pip-tools)
```powershell
pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt
```

### Agora (uv)
```powershell
uv sync
```

## ⚡ Vantagens do UV

1. **Velocidade**: Até 100x mais rápido que pip
2. **Resolução de dependências**: Muito mais eficiente
3. **Lock file automático**: Garante reprodutibilidade
4. **Melhor cache**: Reutiliza pacotes entre projetos
5. **Gerenciamento de versões Python**: Pode instalar diferentes versões do Python
6. **Compatível com pip**: Lê arquivos requirements.txt quando necessário

## 🛠️ TA-Lib Local

Se você precisar instalar o TA-Lib a partir do arquivo wheel local:

```powershell
uv pip install _Arquivos/TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
```

## 📝 Workflow Recomendado

1. **Instalar o uv** (uma vez)
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Sincronizar o ambiente** (sempre que clonar ou atualizar)
   ```powershell
   uv sync
   ```

3. **Ativar o ambiente**
   ```powershell
   .\activate.bat
   ```

4. **Executar scripts**
   ```powershell
   python src/run_webapp.py
   # ou
   uv run python src/run_webapp.py
   ```

## 🔗 Referências

- [Documentação oficial do uv](https://github.com/astral-sh/uv)
- [Guia de migração](https://docs.astral.sh/uv/guides/integration/alternative-tools/)

## ⚠️ Observações

- O `uv` é compatível com pip, então comandos como `pip install` ainda funcionarão no ambiente
- Os arquivos `requirements.in` e `requirements.txt` foram **removidos** - não são mais necessários
- O `pyproject.toml` é agora a **única fonte de verdade** para dependências
- O `uv.lock` será gerado automaticamente no primeiro `uv sync` e deve ser versionado
