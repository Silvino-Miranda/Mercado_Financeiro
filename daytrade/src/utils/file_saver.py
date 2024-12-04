import os
from datetime import datetime


# Função para gerar o conteúdo do arquivo Markdown
def generate_md_content(ticker, decisions):
    content = f"# Decisões para o ativo: {ticker}\n\n"
    for agent, decision in decisions.items():
        if agent != "Ticker":
            content += f"## {agent}\n"
            content += f"**Decisão**: {decision['decisao']}\n\n"
            content += f"**Motivo**: {decision['motivo']}\n\n"
    return content


# Função para salvar o arquivo Markdown
def save_decisions_as_md(ticker, decisions):
    # Gera o conteúdo do arquivo Markdown
    md_content = generate_md_content(ticker, decisions)

    # Cria a pasta resultados, se não existir
    os.makedirs("resultados", exist_ok=True)

    # Pega a data atual no formato YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Nomeia o arquivo com o formato YYYY-MM-DD_ticker.md
    file_name = f"{current_date}_{ticker}.md"

    # Caminho completo do arquivo
    file_path = os.path.join("resultados", file_name)

    # Salva o arquivo .md
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Decisões geradas e salvas com sucesso em: {file_path}")
