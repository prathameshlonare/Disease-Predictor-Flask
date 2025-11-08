# 🩺 Disease Prediction and Hospital Recommendation App 🏥

This project is a web application that predicts potential diseases based on user-provided symptoms and recommends nearby hospitals. It leverages machine learning to analyze symptom patterns and provide informed predictions, helping users make timely decisions about their health.

🚀 **Key Features**

*   **Symptom-Based Prediction:** Predicts potential diseases based on user-entered symptoms.
*   **Hospital Recommendation:** Recommends nearby hospitals based on the predicted disease.
*   **User-Friendly Interface:** Provides a simple and intuitive web interface for easy interaction.
*   **Machine Learning Powered:** Uses a pre-trained machine learning model for accurate disease prediction.
*   **Configurable Parameters:** Allows customization of prediction thresholds and data sources.
*   **Data-Driven:** Uses a data dictionary to map symptoms to numerical indices for model input.
*   **Logging:** Logs application events for debugging and monitoring.

🛠️ **Tech Stack**

*   **Frontend:** HTML, CSS, JavaScript (likely within the `index.html` template)
*   **Backend:** Python, Flask
*   **Machine Learning:** scikit-learn (likely used for the pre-trained model) , numpy, pandas
*   **Data Serialization:** pickle, json
*   **Other:** logging, os

📦 **Getting Started**

### Prerequisites

*   Python 3.6+
*   pip package manager

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install the dependencies:**

    ```bash
    pip install Flask pandas scikit-learn numpy
    ```

### Running Locally

1.  **Set environment variables (if needed):**
    *   Ensure all the file paths in `app.py` are correct with respect to your local setup.

2.  **Run the application:**

    ```bash
    python app.py
    ```

3.  **Open your web browser and navigate to `http://127.0.0.1:5000/`** (or the address shown in the console).

💻 **Usage**

1.  Open the application in your web browser.
2.  Enter your symptoms in the provided input fields.
3.  Click the "Predict" button.
4.  View the predicted disease and recommended hospitals (if available).

📂 **Project Structure**

```
├── app.py               # Main application file (Flask app)
├── ml_utils.py          # Machine learning utility functions (DiseasePredictor class)
├── data_dict.json       # Dictionary mapping symptoms to numerical indices
├── final_ensemble_model.pkl # Pre-trained machine learning model
├── label_encoder.pkl    # Label encoder for disease labels
├── training_data.csv    # Training data (used for column names)
├── hospital_chandrapur.csv # Hospital data
├── templates/           # HTML templates
│   └── index.html       # Main page template
├── static/              # Static assets (CSS, JavaScript, images) 
│   ├── style.css        # CSS Stylesheet 
└── venv/                # Virtual environment (if created)
```

🤝 **Contributing**

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear, concise messages.
4.  Submit a pull request.



📬 **Contact**

If you have any questions or suggestions, please feel free to contact me at [prathameshlonare9@gmail.com](mailto:prathameshlonare9@gmail.com), [swapnilkumbhare706@gmail.com](mailto:swapnilkumbhare706@gmail.com), [suyogmadavi12@gmail.com](mailto:suyogmadavi12@gmail.com), [mohaktalodhikar@gmail.com](mailto:mohaktalodhikar@gmail.com).

💖 **Thanks**

Thank you for checking out this project! I hope it's helpful.


