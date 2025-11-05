# 🚔 Crime Prediction System - São Paulo

Um sistema completo de predição de crimes baseado em Machine Learning para dados criminais de São Paulo.

## 📋 Visão Geral

Este sistema utiliza algoritmos de Machine Learning para prever:
- **Tipo de Crime** (NATUREZA_APURADA)
- **Localização** (BAIRRO) 
- **Categoria do Crime** (Patrimônio, Pessoa, Drogas, Trânsito, Outros)

### 🎯 Performance dos Modelos
- **Categoria de Crime**: ~75-80% de precisão
- **Tipo de Crime**: ~60-65% de precisão  
- **Localização**: ~45-55% de precisão

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
# Instalar dependências Python
pip install -r requirements.txt
```

### 2. Treinar os Modelos

```bash
# Treinar todos os modelos
python3 crime_prediction.py
```

### 3. Iniciar o Servidor Web

```bash
# Servidor Flask para predições
python3 prediction_server.py
```

### 4. Acessar a Interface

- **Dashboard de Visualização**: http://localhost:5001/dashboard
- **Interface de Predição**: http://localhost:5001/
- **API Status**: http://localhost:5001/api/model-status

## 📊 Features Utilizadas

O modelo considera as seguintes características:

### Temporais
- Ano, mês, dia do mês
- Dia da semana (0=Segunda, 6=Domingo)
- Hora do dia (0-23)
- Período do dia (Manhã, Tarde, Noite, Madrugada)
- Indicador de fim de semana

### Geográficas
- Latitude e longitude (arredondadas para 3 casas decimais)
- Município (sempre S.PAULO no dataset)

### Categóricas
- Período do dia
- Município

## 🤖 Algoritmos Utilizados

O sistema testa múltiplos algoritmos e seleciona o melhor:

1. **Random Forest** - Geralmente o melhor performer
2. **Gradient Boosting** - Boa precisão, mais lento
3. **Logistic Regression** - Baseline rápido

## 📁 Estrutura dos Arquivos

```
PI4/
├── crime_prediction.py      # Script principal de treinamento
├── prediction_server.py     # Servidor Flask para API
├── prediction.html          # Interface web de predição
├── prediction.js           # JavaScript da interface
├── prediction_styles.css   # Estilos da interface
├── requirements.txt        # Dependências Python
├── dados.db               # Banco de dados SQLite
└── crime_models_*.pkl     # Modelos treinados (gerados automaticamente)
```

## 🔮 API de Predição

### Endpoint: POST /api/predict

**Request:**
```json
{
    "data": "2024-11-15",
    "hora": "20:00", 
    "latitude": -23.550520,
    "longitude": -46.633308
}
```

**Response:**
```json
{
    "success": true,
    "predictions": {
        "crime": {
            "prediction": "ROUBO - OUTROS",
            "probabilities": [
                {"label": "ROUBO - OUTROS", "probability": 0.35},
                {"label": "FURTO - OUTROS", "probability": 0.28},
                {"label": "LESÃO CORPORAL DOLOSA", "probability": 0.15}
            ]
        },
        "location": {
            "prediction": "CENTRO",
            "probabilities": [...]
        },
        "category": {
            "prediction": "PATRIMONIO", 
            "probabilities": [...]
        }
    },
    "analysis": {
        "datetime": "2024-11-15 20:00",
        "location": "Lat: -23.551, Lng: -46.633",
        "period": "Noite",
        "weekend": "Não"
    }
}
```

## 📈 Exemplos de Uso

### Usando a Classe Python

```python
from crime_prediction import CrimePredictionModel

# Carregar modelo treinado
model = CrimePredictionModel()
model.load_models()

# Fazer predição
features = {
    'ano': 2024,
    'mes': 11,
    'dia_semana': 5,  # Sábado
    'dia_mes': 15,
    'hora': 20,
    'fim_semana': 1,
    'latitude_rounded': -23.550,
    'longitude_rounded': -46.634,
    'periodo_dia': 'Noite',
    'MUNICIPIO': 'S.PAULO'
}

# Predições
crime_pred, crime_proba = model.predict(features, 'crime')
location_pred, location_proba = model.predict(features, 'location') 
category_pred, category_proba = model.predict(features, 'category')

print(f"Crime previsto: {crime_pred}")
print(f"Local previsto: {location_pred}")
print(f"Categoria: {category_pred}")
```

### Usando a API

```bash
curl -X POST http://localhost:5001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "data": "2024-11-15",
    "hora": "20:00",
    "latitude": -23.550520,
    "longitude": -46.633308
  }'
```

## 🔧 Configuração Avançada

### Retreinar Modelos

```python
# Treinar apenas um tipo específico
model = CrimePredictionModel()
model.load_data()
model.feature_engineering()

# Treinar apenas predição de crimes
model.train_models('crime')
model.evaluate_model('crime')
model.save_models()
```

### Ajustar Hiperparâmetros

Edite o arquivo `crime_prediction.py` na função `train_models()`:

```python
models_to_try = {
    'RandomForest': RandomForestClassifier(
        n_estimators=200,  # Mais árvores
        max_depth=15,      # Profundidade máxima
        random_state=42, 
        n_jobs=-1
    ),
    # ... outros modelos
}
```

## 📊 Interpretação dos Resultados

### Feature Importance
O modelo mostra quais características são mais importantes:

1. **hora** - Hora do dia é muito importante
2. **latitude_rounded** - Localização geográfica
3. **longitude_rounded** - Localização geográfica  
4. **dia_semana** - Dia da semana
5. **mes** - Mês do ano

### Categorias de Crime

- **PATRIMONIO**: Roubos, furtos (maioria dos crimes)
- **PESSOA**: Lesões corporais, homicídios, estupros
- **DROGAS**: Tráfico, porte, apreensão de entorpecentes
- **TRANSITO**: Acidentes de trânsito
- **OUTROS**: Demais tipos de crime

## ⚠️ Limitações e Considerações

### Limitações do Modelo
1. **Dados históricos**: Baseado apenas em dados passados
2. **Qualidade dos dados**: Depende da qualidade do registro policial
3. **Viés geográfico**: Pode haver viés para certas regiões
4. **Fatores externos**: Não considera eventos especiais, mudanças socioeconômicas

### Uso Responsável
- **Não deve substituir** investigação policial profissional
- **Usar apenas** para planejamento preventivo e análise
- **Considerar** o contexto social e econômico
- **Revisar** regularmente com novos dados

## 🔒 Considerações Éticas

- Os modelos podem perpetuar vieses existentes nos dados históricos
- Não devem ser usados para discriminar ou criminalizar comunidades
- Devem ser auditados regularmente para garantir equidade
- Transparência é essencial no uso de IA em segurança pública

## 📚 Referências Técnicas

### Algoritmos
- Random Forest: Breiman, L. (2001)
- Gradient Boosting: Friedman, J. H. (2001)  
- Logistic Regression: Cox, D. R. (1958)

### Bibliotecas
- scikit-learn: Machine Learning em Python
- pandas: Manipulação de dados
- Flask: Framework web Python

## 🆘 Troubleshooting

### Erro: "Modelo não encontrado"
```bash
# Retreinar modelos
python3 crime_prediction.py
```

### Erro: "Dados insuficientes"
```bash
# Verificar banco de dados
python3 -c "import sqlite3; conn = sqlite3.connect('dados.db'); print(conn.execute('SELECT COUNT(*) FROM dadoscriminais').fetchone())"
```

### Erro: "Servidor não inicia"
```bash
# Verificar dependências
pip install -r requirements.txt

# Verificar porta
netstat -tlnp | grep :5001
```

## 📞 Suporte

Para problemas técnicos:
1. Verificar logs do servidor
2. Confirmar que todos os arquivos estão presentes
3. Verificar versões das bibliotecas
4. Testar com dados de exemplo

---

**⚡ Sistema desenvolvido para análise e predição de crimes em São Paulo usando Machine Learning**
