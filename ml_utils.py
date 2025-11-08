import pickle
import json
import pandas as pd
import numpy as np
import os
import logging

# Configure logging for ml_utils
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DiseasePredictor:
    def __init__(self, model_file, encoder_file, data_dict_file, training_data_file):
        self.ensemble_model = None
        self.encoder = None
        self.data_dict = None
        self.symptom_index = None
        self.predictions_classes = None
        self.original_training_columns = None
        self.model_file = model_file
        self.encoder_file = encoder_file
        self.data_dict_file = data_dict_file
        self.training_data_file = training_data_file
        self._load_resources()

    def _load_resources(self):
        """Loads the ML model, encoder, and data dictionary."""
        try:
            # Load original training columns from a small piece of training data
            temp_data_for_cols = pd.read_csv(self.training_data_file).dropna(axis=1, how='all')
            self.original_training_columns = temp_data_for_cols.columns[:-1].tolist() # Exclude the target column
            logging.info(f"Training columns loaded from {self.training_data_file}")

            with open(self.model_file, 'rb') as f:
                self.ensemble_model = pickle.load(f)
            logging.info(f"Model loaded from {self.model_file}")

            with open(self.encoder_file, 'rb') as f:
                self.encoder = pickle.load(f)
            logging.info(f"Encoder loaded from {self.encoder_file}")

            with open(self.data_dict_file, 'r') as f:
                self.data_dict = json.load(f)
            self.symptom_index = self.data_dict.get("symptom_index")
            self.predictions_classes = self.data_dict.get("predictions_classes")
            logging.info(f"Data dictionary loaded from {self.data_dict_file}")

            # Sanity check: Verify symptom index size matches training columns
            if len(self.symptom_index) != len(self.original_training_columns):
                logging.warning("CRITICAL WARNING: Symptom index size does not match training column size.")
                logging.warning("This indicates a mismatch between the training data used to build the model/dict and the data dictionary.")
                logging.warning("Prediction may fail or be inaccurate.")

        except FileNotFoundError as e:
            logging.error(f"Error loading a required file: {e}")
            logging.error("Please ensure all required files (.pkl, .json, training_data.csv) are in the correct directory.")
            self._reset_resources()
        except Exception as e:
            logging.error(f"An unexpected error occurred during file loading: {e}")
            self._reset_resources()

    def _reset_resources(self):
        """Resets all loaded resources to None in case of loading failure."""
        self.ensemble_model = None
        self.encoder = None
        self.data_dict = None
        self.symptom_index = None
        self.predictions_classes = None
        self.original_training_columns = None

    def is_ready(self):
        """Checks if all necessary ML resources are loaded."""
        return all([self.ensemble_model, self.encoder, self.symptom_index, self.predictions_classes, self.original_training_columns])

    def get_prediction_results(self, symptoms_list_snake_case, min_symptoms, target_diseases, confidence_threshold):
        """
        Processes symptoms, makes prediction using the loaded model,
        and formats the results.
        """
        if not self.is_ready():
            return {"status": "Error", "message": "Prediction service is not available due to a loading error. Please check server logs."}

        if len(symptoms_list_snake_case) < min_symptoms:
            return {
                "status": "Insufficient Data",
                "message": f"Please provide at least {min_symptoms} symptoms for a prediction."
            }

        input_data_df = pd.DataFrame(0, index=[0], columns=self.original_training_columns)
        unrecognized_symptoms = []
        recognized_symptoms_count = 0

        for symptom_snake_case in symptoms_list_snake_case:
            if symptom_snake_case in self.original_training_columns:
                input_data_df[symptom_snake_case] = 1
                recognized_symptoms_count += 1
            else:
                unrecognized_symptoms.append(symptom_snake_case)

        if recognized_symptoms_count == 0:
            return {
                "status": "Unrecognized Symptoms",
                "message": f"None of the provided symptoms were recognized by the system. Please check spelling or provide more common symptoms.",
                "unrecognized_symptoms": unrecognized_symptoms
            }

        predicted_disease_encoded = self.ensemble_model.predict(input_data_df)[0]
        predicted_disease_label = self.encoder.inverse_transform([predicted_disease_encoded])[0]

        probabilities = self.ensemble_model.predict_proba(input_data_df)[0]
        try:
            predicted_class_index_in_probs = list(self.encoder.classes_).index(predicted_disease_label)
            prediction_probability = probabilities[predicted_class_index_in_probs] * 100
        except ValueError:
            prediction_probability = 0.0
            logging.warning(f"Predicted label '{predicted_disease_label}' not found in encoder classes.")

        results = {
            "status": "Prediction Successful",
            "predicted_disease_label": predicted_disease_label,
            "probability": f"{prediction_probability:.2f}%",
            "unrecognized_symptoms": unrecognized_symptoms,
            "message": "" # Initialize message
        }

        if prediction_probability < confidence_threshold:
            results["status"] = "Uncertain Diagnosis"
            results["message"] = f"The prediction confidence ({prediction_probability:.2f}%) is below the threshold. Please consult a healthcare professional for a definitive diagnosis."
            results["Hospital Recommendations"] = []
        elif predicted_disease_label in target_diseases:
            results["message"] = f"Based on the symptoms provided, you may have {predicted_disease_label}."
        else:
            results["message"] = f"The system predicted '{predicted_disease_label}'. This model is specifically trained for {', '.join(target_diseases)}. Please consult a healthcare professional."
            results["Hospital Recommendations"] = []

        return results

class HospitalRecommender:
    def __init__(self, hospital_data_path):
        self.hospital_data = None
        self.hospital_data_path = hospital_data_path
        self._load_hospital_data()

    def _load_hospital_data(self):
        """Loads hospital data from CSV."""
        if os.path.exists(self.hospital_data_path):
            try:
                self.hospital_data = pd.read_csv(self.hospital_data_path)
                logging.info(f"Hospital data loaded from {self.hospital_data_path}.")
            except Exception as e:
                logging.error(f"Error loading hospital data from {self.hospital_data_path}: {e}")
                self.hospital_data = None
        else:
            logging.warning(f"Hospital data file not found at {self.hospital_data_path}. Hospital recommendations will not be available.")
            self.hospital_data = None

    def recommend_hospitals(self, disease_name, num_recommendations=3):
        """Recommends hospitals based on disease specialty from the loaded data."""
        if self.hospital_data is None:
            return ["Hospital recommendations not available due to data loading error or file not found."]

        if 'Specialties' not in self.hospital_data.columns:
            logging.warning("Warning: 'Specialties' column not found in hospital data.")
            return ["Hospital recommendations not available: 'Specialties' column missing."]

        search_term = disease_name.lower()
        filtered_hospitals = self.hospital_data[
            self.hospital_data['Specialties'].astype(str).str.contains(search_term, case=False, na=False)
        ]

        if filtered_hospitals.empty:
            return [f"No hospitals found specializing in '{disease_name}' in the provided data."]

        recommendations = []
        required_cols = ['Hospital_Name', 'Address', 'Contact']
        if not all(col in filtered_hospitals.columns for col in required_cols):
            logging.warning(f"Warning: Required columns {required_cols} not found in hospital data.")
            return ["Hospital recommendations not available: Required columns missing."]

        try:
            selected_hospitals = filtered_hospitals.sample(min(num_recommendations, len(filtered_hospitals)))
        except ValueError:
            selected_hospitals = filtered_hospitals

        for _, row in selected_hospitals.iterrows():
            name = row['Hospital_Name'] if pd.notna(row['Hospital_Name']) else "N/A"
            address = row['Address'] if pd.notna(row['Address']) else "N/A"
            contact = row['Contact'] if pd.notna(row['Contact']) else "N/A"
            recommendations.append(
                f"{name} (Address: {address}, Contact: {contact})"
            )

        return recommendations

def format_symptom_input(symptom_string):
    """Cleans and formats the symptom input string."""
    if not isinstance(symptom_string, str) or not symptom_string.strip():
        return [] # Return empty list for invalid or empty input

    # Convert to lowercase, replace spaces with underscores, strip whitespace, filter empty
    symptoms = [s.strip().replace(" ", "_").lower() for s in symptom_string.split(",") if s.strip()]
    return symptoms