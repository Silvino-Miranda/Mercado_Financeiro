# Mercado Financeiro - Projetos de Trading e Análise

## 🚀 Descrição Geral
Coleção abrangente de projetos focados em trading automatizado, análise de mercado financeiro e desenvolvimento de estratégias quantitativas. Inclui desde sistemas básicos de backtest até robôs de trading com inteligência artificial.

## 🎯 Objetivo do Repositório
Fornecer uma biblioteca completa de ferramentas e sistemas para:
- Análise técnica e fundamental de ativos
- Desenvolvimento e validação de estratégias de trading
- Automação de operações financeiras
- Educação em finanças quantitativas

## 📁 Estrutura dos Projetos

### 🤖 Trading Automatizado
- **[1-Lucro-Online-Ainda-Hoje](./1-Lucro-Online-Ainda-Hoje/)** - Sistema de backtest para Forex com MME
- **[robo_cripto](./robo_cripto/)** - Robô de trading para criptomoedas
- **[robo_cripto_clean_arch](./robo_cripto_clean_arch/)** - Robô com Clean Architecture
- **[order-binance](./order-binance/)** - Sistema automatizado de ordens na Binance
- **[RN_Operar_Cripto](./RN_Operar_Cripto/)** - Trading com Redes Neurais LSTM

### 📊 Análise e Backtest
- **[Backtest-Cripto](./Backtest-Cripto/)** - Backtest de portfólios de criptomoedas
- **[MA200](./MA200/)** - Estratégia baseada em Média Móvel 200
- **[Dollar-Cost_Averaging_DCA](./Dollar-Cost_Averaging_DCA/)** - Análise de DCA em criptos
- **[Analise de dividendos da carteira](./Analise%20de%20dividendos%20da%20carteira/)** - Análise de dividendos B3

### 🎨 Dashboards e Visualização
- **[Dashboard](./Dashboard/)** - Dashboard interativo com Streamlit
- **[daytrade](./daytrade/)** - Sistema de day trade com IA (OpenAI)

### 🎓 Projetos Acadêmicos
- **[_Teste_de_terceiro/Tech_Challenge_Fase_2](./_Teste_de_terceiro/Tech_Challenge_Fase_2/)** - ML para previsão do Ibovespa

## 🛠️ Tecnologias Utilizadas

### Linguagens e Frameworks
- **Python** - Linguagem principal
- **Jupyter Notebooks** - Análise exploratória
- **Streamlit** - Dashboards interativos

### Bibliotecas Principais
- **Pandas/NumPy** - Manipulação de dados
- **Scikit-learn** - Machine Learning
- **TensorFlow** - Deep Learning (LSTM)
- **YFinance** - Dados financeiros
- **TA-Lib** - Análise técnica
- **Matplotlib/Plotly** - Visualizações

### APIs e Integrações
- **Binance API** - Trading de criptomoedas
- **CCXT** - Multi-exchange connector
- **OpenAI API** - Análise com IA
- **Yahoo Finance** - Dados históricos

## 🚀 Início Rápido

### Pré-requisitos
```bash
# Python 3.8+
python --version

# Git
git --version
```

### Clonagem do Repositório
```bash
git clone https://github.com/Silvino-Miranda/Mercado_Financeiro.git
cd Mercado_Financeiro
```

### Instalação de Dependências
Cada projeto tem seu próprio `requirements.txt`:
```bash
# Exemplo para um projeto específico
cd projeto-escolhido/
pip install -r requirements.txt
```

### Configuração de APIs (quando necessário)
```bash
# Variáveis de ambiente para projetos que usam APIs
export BINANCE_API_KEY="sua_chave"
export BINANCE_API_SECRET="seu_secret"
export OPENAI_API_KEY="sua_chave_openai"
```

## 📊 Projetos por Categoria

### 🔰 Iniciante
1. **Analise de dividendos da carteira** - Análise simples de dividendos
2. **Backtest-Cripto** - Backtest básico de portfólios
3. **Dollar-Cost_Averaging_DCA** - Estratégia DCA

### 🔶 Intermediário
1. **MA200** - Estratégia de média móvel
2. **1-Lucro-Online-Ainda-Hoje** - Backtest Forex
3. **Dashboard** - Interface visual interativa

### 🔴 Avançado
1. **RN_Operar_Cripto** - Trading com IA/ML
2. **robo_cripto_clean_arch** - Arquitetura empresarial
3. **daytrade** - IA com OpenAI para análise

## 🎯 Casos de Uso por Perfil

### 📚 Estudantes e Iniciantes
- Análise de dividendos para carteira pessoal
- Backtest de estratégias simples
- Visualização de dados financeiros

### 💼 Traders e Analistas
- Desenvolvimento de estratégias personalizadas
- Backtesting avançado com múltiplos ativos
- Automação de operações

### 🏢 Desenvolvedores e Empresas
- Sistemas de trading escaláveis
- Arquiteturas limpas para produção
- Integração com múltiplas exchanges

## 📈 Estratégias Implementadas

### Análise Técnica
- **Médias Móveis** (SMA, EMA, MA200)
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**
- **Stochastic Oscillator**

### Estratégias de Investimento
- **Buy and Hold**
- **Dollar-Cost Averaging (DCA)**
- **Mean Reversion**
- **Trend Following**
- **Arbitragem**

### Machine Learning
- **Regressão Logística**
- **Random Forest**
- **Redes Neurais LSTM**
- **Time Series Analysis**

## ⚠️ Avisos Importantes

### Responsabilidade
- **Não constitui aconselhamento financeiro**
- **Use apenas para fins educacionais**
- **Teste em ambiente sandbox primeiro**
- **Nunca invista mais do que pode perder**

### Riscos
- **Alta volatilidade** dos mercados financeiros
- **Possibilidade de perdas significativas**
- **Necessidade de monitoramento constante**
- **Dependência de APIs externas**

## 🤝 Contribuindo

### Como Contribuir
1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Commit** suas mudanças
4. **Push** para a branch
5. **Abra** um Pull Request

### Áreas de Contribuição
- 🐛 **Bug fixes**
- ✨ **Novas funcionalidades**
- 📚 **Documentação**
- 🧪 **Testes**
- 🎨 **Interface/UX**

### Guidelines
- Mantenha código limpo e documentado
- Inclua testes quando possível
- Atualize a documentação
- Siga padrões de commits convencionais

## 📊 Estatísticas do Repositório

### Projetos por Tipo
- **Trading Bots**: 4 projetos
- **Backtest Systems**: 4 projetos
- **Analysis Tools**: 3 projetos
- **Dashboards**: 2 projetos
- **Academic**: 1 projeto

### Tecnologias Mais Usadas
- **Python**: 100% dos projetos
- **Pandas**: 90% dos projetos
- **APIs Financeiras**: 70% dos projetos
- **Machine Learning**: 40% dos projetos
- **Streamlit**: 20% dos projetos

## 🗺️ Roadmap Futuro

### Próximas Funcionalidades
- [ ] Sistema unificado de configuração
- [ ] Dashboard central para todos os projetos
- [ ] Integração com mais exchanges
- [ ] Backtesting unificado
- [ ] Sistema de notificações

### Melhorias Planejadas
- [ ] Testes automatizados
- [ ] CI/CD pipeline
- [ ] Documentação interativa
- [ ] Containerização com Docker
- [ ] Monitoramento de performance

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor
**Silvino Miranda**
- GitHub: [@Silvino-Miranda](https://github.com/Silvino-Miranda)
- LinkedIn: [Silvino Miranda](https://linkedin.com/in/silvino-miranda)

## 🙏 Agradecimentos
- Comunidade Python
- Contribuidores do projeto
- Provedores de APIs financeiras
- Desenvolvedores de bibliotecas open source

---

⭐ **Se este repositório foi útil, considere dar uma estrela!**