import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class CrimePredictionModel:
    def __init__(self, db_path='dados.db'):
        self.db_path = db_path
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.feature_names = []

    def load_data(self):
        """Load data from SQLite database"""
        print("📊 Carregando dados do banco de dados...")

        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT 
            NUM_BO,
            DATA_OCORRENCIA_BO,
            HORA_OCORRENCIA_BO,
            NATUREZA_APURADA,
            LATITUDE,
            LONGITUDE,
            MUNICIPIO,
            BAIRRO
        FROM dadoscriminais
        WHERE 
            DATA_OCORRENCIA_BO != '' 
            AND HORA_OCORRENCIA_BO != ''
            AND BAIRRO != ''
            AND NATUREZA_APURADA != ''
            AND LATITUDE != 0.0
            AND LONGITUDE != 0.0
        LIMIT 100000
        """

        self.df = pd.read_sql_query(query, conn)
        conn.close()

        print(f"✅ Dados carregados: {len(self.df):,} registros")
        return self.df

    def feature_engineering(self):
        """Create features from the raw data"""
        print("🔧 Criando features...")

        # Convert date columns
        self.df['DATA_OCORRENCIA_BO'] = pd.to_datetime(self.df['DATA_OCORRENCIA_BO'])

        # Extract time features
        self.df['ano'] = self.df['DATA_OCORRENCIA_BO'].dt.year
        self.df['mes'] = self.df['DATA_OCORRENCIA_BO'].dt.month
        self.df['dia_semana'] = self.df['DATA_OCORRENCIA_BO'].dt.dayofweek
        self.df['dia_mes'] = self.df['DATA_OCORRENCIA_BO'].dt.day

        # Extract hour from time string
        def extract_hour(time_str):
            try:
                if ':' in str(time_str):
                    return int(str(time_str).split(':')[0])
                return 12
            except:
                return 12

        self.df['hora'] = self.df['HORA_OCORRENCIA_BO'].apply(extract_hour)

        # Create time periods
        def get_period(hour):
            if 6 <= hour < 12:
                return 'Manhã'
            elif 12 <= hour < 18:
                return 'Tarde'
            elif 18 <= hour < 24:
                return 'Noite'
            else:
                return 'Madrugada'

        self.df['periodo_dia'] = self.df['hora'].apply(get_period)

        # Weekend indicator
        self.df['fim_semana'] = (self.df['dia_semana'] >= 5).astype(int)

        # Geographic features
        self.df['latitude_rounded'] = self.df['LATITUDE'].round(3)
        self.df['longitude_rounded'] = self.df['LONGITUDE'].round(3)

        # Crime category grouping
        def categorize_crime(crime_type):
            crime_upper = str(crime_type).upper()
            if any(word in crime_upper for word in ['ROUBO', 'FURTO']):
                return 'PATRIMONIO'
            elif any(word in crime_upper for word in ['LESÃO', 'HOMICÍDIO', 'ESTUPRO']):
                return 'PESSOA'
            elif any(word in crime_upper for word in ['TRÁFICO', 'PORTE', 'APREENSÃO']):
                return 'DROGAS'
            elif any(word in crime_upper for word in ['TRÂNSITO', 'ACIDENTE']):
                return 'TRANSITO'
            else:
                return 'OUTROS'

        self.df['categoria_crime'] = self.df['NATUREZA_APURADA'].apply(categorize_crime)

        print("✅ Features criadas com sucesso!")

    def prepare_features(self, target_type='crime'):
        """Prepare features for training"""
        print(f"🎯 Preparando features para predição de {target_type}...")

        # Select features for training
        feature_columns = [
            'ano', 'mes', 'dia_semana', 'dia_mes', 'hora',
            'fim_semana', 'latitude_rounded', 'longitude_rounded'
        ]

        # Add categorical features
        categorical_features = ['periodo_dia', 'MUNICIPIO']

        # Prepare feature matrix
        X_numeric = self.df[feature_columns].copy()

        # Encode categorical features
        X_categorical = pd.DataFrame()
        for col in categorical_features:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                X_categorical[f'{col}_encoded'] = self.encoders[col].fit_transform(self.df[col])
            else:
                X_categorical[f'{col}_encoded'] = self.encoders[col].transform(self.df[col])

        # Combine features
        X = pd.concat([X_numeric, X_categorical], axis=1)

        # Scale features
        if target_type not in self.scalers:
            self.scalers[target_type] = StandardScaler()
            X_scaled = pd.DataFrame(
                self.scalers[target_type].fit_transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            X_scaled = pd.DataFrame(
                self.scalers[target_type].transform(X),
                columns=X.columns,
                index=X.index
            )

        # Prepare target variable
        if target_type == 'crime':
            y = self.df['NATUREZA_APURADA']
        elif target_type == 'location':
            y = self.df['BAIRRO']
        elif target_type == 'category':
            y = self.df['categoria_crime']

        # Encode target if needed
        target_encoder = f'{target_type}_encoder'
        if target_encoder not in self.encoders:
            self.encoders[target_encoder] = LabelEncoder()
            y_encoded = self.encoders[target_encoder].fit_transform(y)
        else:
            y_encoded = self.encoders[target_encoder].transform(y)

        self.feature_names = X_scaled.columns.tolist()

        return X_scaled, y_encoded, y

    def train_models(self, target_type='crime', test_size=0.2):
        """Train multiple models and select the best one"""
        print(f"🚀 Treinando modelos para predição de {target_type}...")

        # Prepare data
        X, y_encoded, y_original = self.prepare_features(target_type)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )

        # Define models to try
        models_to_try = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'GradientBoosting': GradientBoostingClassifier(n_estimators=50, random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000)
        }

        best_score = 0
        best_model_name = None

        # Train and evaluate models
        for name, model in models_to_try.items():
            print(f"  📈 Treinando {name}...")

            # Train model
            model.fit(X_train, y_train)

            # Test score
            test_score = model.score(X_test, y_test)

            print(f"    Test Score: {test_score:.4f}")

            # Save model results
            self.models[f'{target_type}_{name}'] = {
                'model': model,
                'test_score': test_score,
                'X_test': X_test,
                'y_test': y_test
            }

            if test_score > best_score:
                best_score = test_score
                best_model_name = name

        # Set best model as default
        self.models[f'{target_type}_best'] = self.models[f'{target_type}_{best_model_name}']

        print(f"✅ Melhor modelo para {target_type}: {best_model_name} (Score: {best_score:.4f})")

        return best_model_name, best_score

    def predict(self, features_dict, target_type='crime', model_name='best'):
        """Make predictions using trained model"""
        model_key = f'{target_type}_{model_name}'
        if model_key not in self.models:
            print(f"❌ Modelo {model_key} não encontrado!")
            return None

        model = self.models[model_key]['model']

        # Convert input to DataFrame
        input_df = pd.DataFrame([features_dict])

        # Apply same transformations
        X_input = self._prepare_prediction_features(input_df, target_type)

        # Make prediction
        prediction_encoded = model.predict(X_input)[0]
        prediction_proba = model.predict_proba(X_input)[0]

        # Decode prediction
        encoder_key = f'{target_type}_encoder'
        if encoder_key in self.encoders:
            prediction = self.encoders[encoder_key].inverse_transform([prediction_encoded])[0]

            # Get top predictions with probabilities
            top_indices = np.argsort(prediction_proba)[::-1][:5]
            top_predictions = []
            for idx in top_indices:
                label = self.encoders[encoder_key].inverse_transform([idx])[0]
                prob = prediction_proba[idx]
                top_predictions.append((label, prob))

            return prediction, top_predictions

        return prediction_encoded, prediction_proba

    def _prepare_prediction_features(self, input_df, target_type):
        """Prepare features for prediction (same as training)"""
        # Apply same feature engineering
        feature_columns = [
            'ano', 'mes', 'dia_semana', 'dia_mes', 'hora',
            'fim_semana', 'latitude_rounded', 'longitude_rounded'
        ]

        X_numeric = input_df[feature_columns].copy()

        # Encode categorical features
        X_categorical = pd.DataFrame()
        categorical_features = ['periodo_dia', 'MUNICIPIO']

        for col in categorical_features:
            if f'{col}_encoded' in self.feature_names:
                X_categorical[f'{col}_encoded'] = self.encoders[col].transform(input_df[col])

        # Combine features
        X = pd.concat([X_numeric, X_categorical], axis=1)

        # Scale features
        X_scaled = pd.DataFrame(
            self.scalers[target_type].transform(X),
            columns=X.columns,
            index=X.index
        )

        return X_scaled

    def save_models(self, filepath_prefix='crime_models'):
        """Save trained models and encoders"""
        print(f"💾 Salvando modelos...")

        try:
            # Save models
            joblib.dump(self.models, f'{filepath_prefix}_models.pkl')
            print(f"✅ Modelos salvos: {filepath_prefix}_models.pkl")
        except Exception as e:
            print(f"❌ Erro ao salvar modelos: {e}")

        try:
            joblib.dump(self.encoders, f'{filepath_prefix}_encoders.pkl')
            print(f"✅ Encoders salvos: {filepath_prefix}_encoders.pkl")
        except Exception as e:
            print(f"❌ Erro ao salvar encoders: {e}")

        try:
            joblib.dump(self.scalers, f'{filepath_prefix}_scalers.pkl')
            print(f"✅ Scalers salvos: {filepath_prefix}_scalers.pkl")
        except Exception as e:
            print(f"❌ Erro ao salvar scalers: {e}")

        try:
            joblib.dump(self.feature_names, f'{filepath_prefix}_features.pkl')
            print(f"✅ Features salvos: {filepath_prefix}_features.pkl")
        except Exception as e:
            print(f"❌ Erro ao salvar features: {e}")

        print(f"✅ Processo de salvamento concluído!")

    def load_models(self, filepath_prefix='crime_models'):
        """Load trained models and encoders"""
        try:
            self.models = joblib.load(f'{filepath_prefix}_models.pkl')
            self.encoders = joblib.load(f'{filepath_prefix}_encoders.pkl')
            self.scalers = joblib.load(f'{filepath_prefix}_scalers.pkl')
            self.feature_names = joblib.load(f'{filepath_prefix}_features.pkl')
            print(f"✅ Modelos carregados de: {filepath_prefix}")
            return True
        except FileNotFoundError:
            print(f"❌ Arquivos de modelo não encontrados: {filepath_prefix}")
            return False


def main():
    """Main training pipeline"""
    print("🚔 Crime Prediction Model - São Paulo")
    print("=" * 50)

    # Initialize model
    crime_model = CrimePredictionModel()

    # Load and prepare data
    crime_model.load_data()
    crime_model.feature_engineering()

    print(f"\n📈 Dataset Info:")
    print(f"  Total de registros: {len(crime_model.df):,}")
    print(f"  Período: {crime_model.df['DATA_OCORRENCIA_BO'].min()} até {crime_model.df['DATA_OCORRENCIA_BO'].max()}")
    print(f"  Tipos de crime únicos: {crime_model.df['NATUREZA_APURADA'].nunique()}")
    print(f"  Bairros únicos: {crime_model.df['BAIRRO'].nunique()}")

    # Train models for different targets
    targets_to_train = ['category', 'crime', 'location']

    for target in targets_to_train:
        print(f"\n{'='*20} TREINANDO {target.upper()} {'='*20}")
        try:
            best_model, best_score = crime_model.train_models(target)
        except Exception as e:
            print(f"❌ Erro ao treinar modelo para {target}: {e}")

    # Save models
    crime_model.save_models()

    # Example predictions
    print(f"\n{'='*20} EXEMPLOS DE PREDIÇÃO {'='*20}")

    # Example 1: Weekend evening in a central area
    example_features = {
        'ano': 2024,
        'mes': 11,
        'dia_semana': 5,  # Saturday
        'dia_mes': 15,
        'hora': 20,  # 8 PM
        'fim_semana': 1,
        'latitude_rounded': -23.550,
        'longitude_rounded': -46.634,
        'periodo_dia': 'Noite',
        'MUNICIPIO': 'S.PAULO'
    }

    print("\n🔮 Exemplo de Predição:")
    print("Cenário: Sábado à noite no centro de São Paulo")

    # Predict crime type
    try:
        crime_pred, crime_proba = crime_model.predict(example_features, 'crime')
        print(f"\n🚨 Tipo de Crime Mais Provável: {crime_pred}")
        print("Top 3 probabilidades:")
        for i, (crime, prob) in enumerate(crime_proba[:3]):
            print(f"  {i+1}. {crime}: {prob:.3f}")
    except Exception as e:
        print(f"Erro na predição de crime: {e}")

    # Predict location
    try:
        location_pred, location_proba = crime_model.predict(example_features, 'location')
        print(f"\n📍 Bairro Mais Provável: {location_pred}")
        print("Top 3 probabilidades:")
        for i, (location, prob) in enumerate(location_proba[:3]):
            print(f"  {i+1}. {location}: {prob:.3f}")
    except Exception as e:
        print(f"Erro na predição de localização: {e}")

    # Predict category
    try:
        category_pred, category_proba = crime_model.predict(example_features, 'category')
        print(f"\n📊 Categoria Mais Provável: {category_pred}")
        print("Top 3 probabilidades:")
        for i, (category, prob) in enumerate(category_proba[:3]):
            print(f"  {i+1}. {category}: {prob:.3f}")
    except Exception as e:
        print(f"Erro na predição de categoria: {e}")

    print(f"\n✅ Treinamento concluído! Modelos salvos.")
    print(f"📖 Use a classe CrimePredictionModel para fazer novas predições.")


if __name__ == "__main__":
    main()
