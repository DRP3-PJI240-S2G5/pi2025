# 🚔 Sistema de Predição de Crimes - São Paulo

Sistema inteligente de predição de ocorrências criminais em São Paulo utilizando Machine Learning e análise de dados geoespaciais.

## 📋 Descrição

Este projeto implementa um sistema completo de predição de crimes que utiliza algoritmos de Machine Learning para analisar padrões criminais e fazer predições baseadas em localização, data e hora. O sistema inclui uma interface web interativa e um dashboard para visualização de dados.

## ✨ Funcionalidades

- 🔮 **Predição Inteligente**: Predição de tipos de crime baseada em localização, data e hora
- 📊 **Dashboard Interativo**: Visualização de dados criminais com gráficos e estatísticas
- 🗺️ **Análise Geoespacial**: Predição baseada em coordenadas geográficas (latitude/longitude)
- 📈 **Múltiplos Modelos**: Predição de tipo de crime, localização e categoria
- 🌐 **Interface Web**: Interface moderna e responsiva para facilitar o uso
- 📱 **Design Responsivo**: Funciona em desktop, tablet e dispositivos móveis

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.x, Flask
- **Machine Learning**: scikit-learn, pandas, numpy
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Banco de Dados**: SQLite
- **Visualização**: Chart.js
- **Styling**: CSS Grid, Flexbox, Gradientes

## 🚀 Como Usar

### 1. Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd PI4

# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar o Sistema

```bash
# Iniciar o servidor
python prediction_server.py
```

O servidor será iniciado em: **http://localhost:5001**

### 3. Acessar as Interfaces

- **🔮 Interface de Predição**: http://localhost:5001/
- **📊 Dashboard**: http://localhost:5001/dashboard
- **🔧 Status da API**: http://localhost:5001/api/model-status

## 💻 Como Fazer Predições

1. **Acesse a Interface**: Abra http://localhost:5001/ no navegador
2. **Preencha os Dados**:
   - Data e hora do evento
   - Latitude e longitude da localização
   - Bairro (opcional)
3. **Execute a Predição**: Clique em "🔮 Fazer Predição"
4. **Analise os Resultados**: Veja as predições de tipo de crime, localização e categoria

### Exemplo de Uso

```
Data: 2024-11-15
Hora: 20:00
Latitude: -23.550520
Longitude: -46.633308
Bairro: Centro
```

## 📁 Estrutura do Projeto

```
PI4/
├── 📄 prediction_server.py     # Servidor Flask principal
├── 🤖 crime_prediction.py     # Modelo de Machine Learning
├── 🌐 prediction.html         # Interface de predição
├── 📊 dashboard.html          # Dashboard de dados
├── 🎨 prediction_styles.css   # Estilos da interface
├── 📱 prediction.js           # JavaScript da interface
├── 🗃️ dados.db               # Base de dados SQLite
├── 📋 requirements.txt        # Dependências Python
├── 🔧 extract_data.py         # Script de extração de dados
├── 📈 Modelos treinados:
│   ├── crime_models_models.pkl    # Modelos ML
│   ├── crime_models_encoders.pkl  # Encoders
│   ├── crime_models_scalers.pkl   # Escaladores
│   └── crime_models_features.pkl  # Features
├── 📊 Dados processados:
│   ├── crime_types.csv
│   ├── monthly_trends.csv
│   ├── top_neighborhoods.csv
│   └── dashboard_data.json
└── 📚 Documentação:
    ├── README.md              # Este arquivo
    └── ML_README.md           # Documentação técnica ML
```

## 🔧 API Endpoints

### Predição de Crimes
```http
POST /api/predict
Content-Type: application/json

{
  "data": "2024-11-15",
  "hora": "20:00",
  "latitude": -23.550520,
  "longitude": -46.633308,
  "bairro": "Centro"
}
```

### Status dos Modelos
```http
GET /api/model-status
```

### Dashboard Data
```http
GET /api/dashboard-data
```

## 🧠 Modelos de Machine Learning

O sistema utiliza múltiplos modelos para diferentes tipos de predição:

1. **Predição de Tipo de Crime**: Classifica o tipo provável de crime
2. **Predição de Localização**: Prediz a região/bairro mais provável
3. **Predição de Categoria**: Categoriza o crime em grupos principais

### Features Utilizadas
- Coordenadas geográficas (latitude, longitude)
- Informações temporais (hora, dia da semana, mês)
- Dados categóricos do local
- Padrões históricos de criminalidade

## 📊 Dashboard

O dashboard oferece visualizações interativas incluindo:

- 📈 **Tendências Mensais**: Evolução dos crimes ao longo do tempo
- 🏆 **Top Bairros**: Bairros com maior incidência criminal
- 🎯 **Tipos de Crime**: Distribuição por categorias
- 📍 **Análise Geoespacial**: Mapas de calor das ocorrências

## 🛡️ Segurança e Privacidade

- Dados processados de forma anônima
- Não armazenamento de informações pessoais
- Uso apenas para fins educacionais e de pesquisa

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é para fins educacionais e de pesquisa.

## 🐛 Resolução de Problemas

### Erro 404 na Interface
- Verifique se o servidor está rodando em http://localhost:5001
- Confirme que o arquivo `prediction.html` existe

### Modelos não Carregados
- Execute o script de treinamento: `python crime_prediction.py`
- Verifique se os arquivos `.pkl` foram gerados

### Problemas de Porta
- Se a porta 5001 estiver ocupada, altere no `prediction_server.py`
- Use `lsof -i :5001` para verificar processos usando a porta

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação técnica em `ML_README.md`
2. Consulte os logs do servidor para erros
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando Python, Flask e Machine Learning**

*Sistema de Predição de Crimes - São Paulo | 2024-2025*
