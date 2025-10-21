"""
Helper script para atualizar referências de colunas para lowercase
Mapeia nomes antigos (CSV) para novos (banco de dados)
"""

# Mapeamento de colunas
COLUMN_MAP = {
    "'Data'": "'data'",
    "'Operacao'": "'operacao'",
    "'Status'": "'status'",
    "'Previsao'": "'previsao'",
    "'Valor Atual'": "'valor_atual'",
    "'Preco'": "'preco'",
    "'Quantidade'": "'quantidade'",
    "'Custo'": "'custo'",
    "'Capital'": "'capital'"
}

def update_columns_in_file(file_path: str):
    """Atualiza referências de colunas no arquivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Substituir cada coluna
    for old, new in COLUMN_MAP.items():
        content = content.replace(f"[{old}]", f"[{new}]")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Arquivo atualizado: {file_path}")
        return True
    else:
        print(f"ℹ️  Nenhuma alteração necessária em: {file_path}")
        return False

if __name__ == '__main__':
    file_path = 'src/webapp/models/trading_data_model.py'
    update_columns_in_file(file_path)
