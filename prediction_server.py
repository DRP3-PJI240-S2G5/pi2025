from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import sqlite3
from crime_prediction import CrimePredictionModel
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Global variable to store the trained model
crime_model = None

def load_or_train_model():
    """Load existing model or train a new one"""
    global crime_model

    if crime_model is None:
        crime_model = CrimePredictionModel()

        # Try to load existing models
        if not crime_model.load_models():
            print("🚀 Modelos não encontrados. Treinando novos modelos...")

            # Load and prepare data
            crime_model.load_data()
            crime_model.feature_engineering()

            # Train models for different targets
            targets_to_train = ['crime', 'location', 'category']

            for target in targets_to_train:
                print(f"Treinando modelo para {target}...")
                try:
                    crime_model.train_models(target)
                except Exception as e:
                    print(f"Erro ao treinar modelo para {target}: {e}")

            # Save models
            crime_model.save_models()
            print("✅ Modelos treinados e salvos!")

    return crime_model

@app.route('/')
def index():
    """Serve the main prediction page"""
    return send_from_directory('.', 'prediction.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/api/predict', methods=['POST'])
def predict_crime():
    """API endpoint for crime prediction"""
    try:
        # Load model if not already loaded
        model = load_or_train_model()

        # Get input data
        data = request.get_json()

        # Parse date and time
        date_str = data.get('data')
        time_str = data.get('hora')

        if not date_str or not time_str:
            return jsonify({'error': 'Data e hora são obrigatórios'}), 400

        # Parse datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M')

        # Extract features
        features = {
            'ano': date_obj.year,
            'mes': date_obj.month,
            'dia_semana': date_obj.weekday(),
            'dia_mes': date_obj.day,
            'hora': time_obj.hour,
            'fim_semana': 1 if date_obj.weekday() >= 5 else 0,
            'latitude_rounded': round(float(data.get('latitude', -23.550)), 3),
            'longitude_rounded': round(float(data.get('longitude', -46.633)), 3),
            'MUNICIPIO': 'S.PAULO'
        }

        # Determine period of day
        hour = time_obj.hour
        if 6 <= hour < 12:
            features['periodo_dia'] = 'Manhã'
        elif 12 <= hour < 18:
            features['periodo_dia'] = 'Tarde'
        elif 18 <= hour < 24:
            features['periodo_dia'] = 'Noite'
        else:
            features['periodo_dia'] = 'Madrugada'

        # Make predictions
        predictions = {}

        # Predict crime type
        try:
            crime_pred, crime_proba = model.predict(features, 'crime')
            predictions['crime'] = {
                'prediction': crime_pred,
                'probabilities': [{'label': label, 'probability': float(prob)}
                                for label, prob in crime_proba[:5]]
            }
        except Exception as e:
            print(f"Erro na predição de crime: {e}")
            predictions['crime'] = {'error': str(e)}

        # Predict location
        try:
            location_pred, location_proba = model.predict(features, 'location')
            predictions['location'] = {
                'prediction': location_pred,
                'probabilities': [{'label': label, 'probability': float(prob)}
                                for label, prob in location_proba[:5]]
            }
        except Exception as e:
            print(f"Erro na predição de localização: {e}")
            predictions['location'] = {'error': str(e)}

        # Predict category
        try:
            category_pred, category_proba = model.predict(features, 'category')
            predictions['category'] = {
                'prediction': category_pred,
                'probabilities': [{'label': label, 'probability': float(prob)}
                                for label, prob in category_proba[:5]]
            }
        except Exception as e:
            print(f"Erro na predição de categoria: {e}")
            predictions['category'] = {'error': str(e)}

        # Add analysis details
        analysis = {
            'input_features': features,
            'datetime': f"{date_str} {time_str}",
            'location': f"Lat: {features['latitude_rounded']}, Lng: {features['longitude_rounded']}",
            'period': features['periodo_dia'],
            'weekend': 'Sim' if features['fim_semana'] else 'Não'
        }

        return jsonify({
            'success': True,
            'predictions': predictions,
            'analysis': analysis
        })

    except Exception as e:
        print(f"Erro na API de predição: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/model-status')
def model_status():
    """Get model training status"""
    try:
        model_files = [
            'crime_models_models.pkl',
            'crime_models_encoders.pkl',
            'crime_models_scalers.pkl',
            'crime_models_features.pkl'
        ]

        models_exist = all(os.path.exists(f) for f in model_files)

        status = {
            'models_trained': models_exist,
            'available_predictions': ['crime', 'location', 'category'] if models_exist else [],
            'model_files': {f: os.path.exists(f) for f in model_files}
        }

        if models_exist:
            # Get some basic stats
            try:
                conn = sqlite3.connect('dados.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM dadoscriminais")
                total_records = cursor.fetchone()[0]
                conn.close()

                status['dataset_info'] = {
                    'total_records': total_records,
                    'database_file': 'dados.db'
                }
            except Exception as e:
                status['dataset_info'] = {'error': str(e)}

        return jsonify(status)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train-models', methods=['POST'])
def train_models():
    """Force retrain models"""
    try:
        global crime_model
        crime_model = None  # Reset model

        # Retrain
        model = load_or_train_model()

        return jsonify({
            'success': True,
            'message': 'Modelos retreinados com sucesso!'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚔 Crime Prediction API Server")
    print("=" * 40)
    print("🌐 Servidor web para predição de crimes")
    print("📊 Dashboard: http://localhost:5001/dashboard")
    print("🔮 Predições: http://localhost:5001/")
    print("🔧 API Status: http://localhost:5001/api/model-status")
    print("\n💡 Pressione Ctrl+C para parar o servidor")

    # Load models on startup (in background)
    try:
        load_or_train_model()
        print("✅ Modelos carregados com sucesso!")
    except Exception as e:
        print(f"⚠️  Aviso: {e}")
        print("🔄 Modelos serão treinados quando necessário")

    app.run(debug=True, host='0.0.0.0', port=5001)
