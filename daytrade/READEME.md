
'''
  py.exe -3.12 -m pip install .\TA_Lib-0.4.32-cp312-cp312-win_amd64.whl --force-reinstall

  pip install ta-lib
'''


### Passo Adicional: Usar um Gerenciador de Dependências
Você pode usar uma ferramenta como `pip-tools` ou `poetry`, que ajuda a gerenciar as dependências e suas versões de forma mais organizada. Isso evita conflitos como esses no futuro.

1. **Instale `pip-tools`**:
   ```bash
   pip install pip-tools
   ```

2. **Crie um arquivo `requirements.in`** com as bibliotecas que você precisa, sem especificar versões:
   ```
   langchain
   langchain-community
   transformers
   tritonclient
   ```

3. **Gere o arquivo `requirements.txt`** com as versões adequadas:
   ```bash
   pip-compile
   ```

4. **Instale as dependências** usando o `requirements.txt` gerado:
   ```bash
   pip install -r requirements.txt
   ```

Seguindo esses passos, você deverá ter um ambiente com as versões corretas das bibliotecas e evitar conflitos futuros.
