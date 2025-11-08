from flask import Flask, render_template, request
import logging
from ml_utils import DiseasePredictor, HospitalRecommender, format_symptom_input

# --- Configuration ---
MODEL_FILE = "final_ensemble_model.pkl"
ENCODER_FILE = "label_encoder.pkl"
DATA_DICT_FILE = "data_dict.json"
TRAINING_DATA_FILE = "training_data.csv"
HOSPITAL_DATA_PATH = "hospital_chandrapur.csv"
MIN_SYMPTOMS = 7 # Minimum symptoms required for prediction
TARGET_DISEASES = ["Dengue", "Malaria", "Typhoid"] # List of diseases the model is specifically for
CONFIDENCE_THRESHOLD = 40.0 # Minimum probability for a confident prediction (in percentage)

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize Predictor and Recommender ---
disease_predictor = DiseasePredictor(MODEL_FILE, ENCODER_FILE, DATA_DICT_FILE, TRAINING_DATA_FILE)
hospital_recommender = HospitalRecommender(HOSPITAL_DATA_PATH)

# --- Flask App Routes ---
app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main page with the symptom input form."""
    # Pass None initially, as no results are available on first load
    return render_template('index.html', results=None, symptom_index=disease_predictor.symptom_index, MIN_SYMPTOMS=MIN_SYMPTOMS)

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the form submission, makes a prediction, and renders the results."""
    if request.method == 'POST':
        symptoms_input_string = request.form.get('symptoms', '')
        symptoms_list_snake_case = format_symptom_input(symptoms_input_string)
        logging.info(f"Symptoms input: {symptoms_list_snake_case}")

        # Get prediction results from the DiseasePredictor
        prediction_results = disease_predictor.get_prediction_results(
            symptoms_list_snake_case,
            MIN_SYMPTOMS,
            TARGET_DISEASES,
            CONFIDENCE_THRESHOLD
        )

        # If prediction was successful and it's a target disease, get hospital recommendations
        if prediction_results.get("status") == "Prediction Successful" and \
          prediction_results.get("predicted_disease_label") in TARGET_DISEASES:
            disease_name = prediction_results.get("predicted_disease_label")
            prediction_results["Hospital Recommendations"] = hospital_recommender.recommend_hospitals(disease_name)
        else:
            # Ensure "Hospital Recommendations" key exists even if empty
            if "Hospital Recommendations" not in prediction_results:
                prediction_results["Hospital Recommendations"] = []

        # Render the same page with the prediction results
        logging.info(f"Prediction results: {prediction_results}")
        return render_template('index.html', results=prediction_results, symptom_index=disease_predictor.symptom_index,  MIN_SYMPTOMS=MIN_SYMPTOMS)

# --- Run Flask App ---
if __name__ == '__main__':
    # Ensure required files are loaded before running the app
    if disease_predictor.is_ready():
        app.run(debug=True, port=5000) # You can change the port if 5000 is in use
    else:
        logging.error("\nFlask app cannot start because required model/data files could not be loaded. Please check the error messages above and ensure all files are correct and present.")
