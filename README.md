# TravelBuddy Pro ✈️

An interactive, AI-powered travel planner for crafting personalized Indian holidays. Built with Streamlit and powered by the Google Gemini API, this app transforms simple user inputs into detailed, actionable, and multi-lingual travel itineraries.

---

## ✨ Features

* AAI-Powered Itineraries: Leverages the Google Gemini API (gemini-2.5-flash) to generate creative and practical travel plans from scratch.
*  Deep Personalization: Tailors every itinerary based on destination, start/end dates, number of travelers, budget, and specific interests.
*  AI Context-Aware Chatbot: Includes an "Ask Anything" chatbot that has your current itinerary in its context, allowing you to ask specific questions about your plan.
*  Dynamic Re-planning: Change your plan on the fly! Select a "Rainy Day ☔" or "Low Energy 😴" option to have the AI generate a new, more suitable plan for any given day.
*  AI Trip Toolkit: Generate a smart AI Packing List based on your itinerary's activities and an AI Local Guide with must-try foods, cultural etiquette, scams, and basic local phrases.
*  Interactive Mapping**: Visualizes the entire trip on an interactive map using Pydeck, pinpointing suggested sights, restaurants, and hotels. 
*  Dynamic Map Filtering**: Focus the map on a specific day's activities with the click of a button for a more "pinpointed" view.
*  Built-in Expense Tracker: A sidebar tool to log expenses, view a running total, and easily split the bill between all travelers.
*  Daily Travel Journal: A dedicated journaling space for each day of your trip to write notes and upload photos, all organized in clean tabs.
*  Multi-Language Support**: Supports itinerary generation in multiple languages, including English, Hindi (हिन्दी), Bengali (বাংলা), and Telugu (తెలుగు), with a focus on vernacular usability.
*  Actionable Links & Safety: Integrates quick-access buttons for booking (Flights, Hotels), services (Uber, Restaurants), and a Medical Emergency button to find nearby hospitals.
*  Detailed Budget Breakdown: Provides an AI-generated table allocating your budget across categories like accommodation, food, and activities.
*  PDF Export**: Allows users to download their complete itinerary as a PDF, with full support for vernacular language characters.



---

## 🛠️ Tech Stack

This project is built with a modern, open-source stack:

* **Frontend**: Streamlit
* **AI Model**: Google Gemini
* **Mapping**: Pydeck & Mapbox
* **Data Handling**: Pandas
* **PDF Generation**: FPDF2
* **Deployment**: Streamlit Community Cloud

---

## 🚀 Getting Started

To run this project on your local machine, follow these steps.

### Prerequisites

* Python 3.8+
* A GitHub account to clone the repository.

### 1. Clone the Repository

git clone https://github.com/Abhinaba925/TravelBuddyPro.git
cd TravelBuddyPro


### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to keep dependencies isolated.

For macOS/Linux
python3 -m venv venv
source venv/bin/activate

For Windows
python -m venv venv
.\venv\Scripts\activate


### 3. Install Dependencies

Install all the required Python libraries from the requirements.txt file.

pip install -r requirements.txt


### 4. Set Up API Keys (Secrets)

The application requires API keys for Google Gemini and Mapbox. For local development, you'll use a `.env` file.

1. Create a new file in the root of your project folder named `.env`
2. Copy the content below into the file and replace the placeholder text with your actual API keys:

.env file
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
MAPBOX_API_TOKEN="pk.eyJ1...YOUR_MAPBOX_PUBLIC_TOKEN_HERE"


### 5. Download the Font for PDF Export

The PDF generation for vernacular languages requires a specific font.

1. **Download the font**: [Noto Sans Devanagari](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari)
2. **Place the file**: Make sure the downloaded `NotoSansDevanagari-Regular.ttf` file is inside the `fonts` folder in your project.

### 6. Run the App

You're all set! Run the following command in your terminal:

streamlit run app.py


---

## ☁️ Deployment

This application is deployed and live on Streamlit Community Cloud.

**Live Demo**: [TravelBuddy Pro App](https://travelbuddypro-nqzhqdsuedvuwgsym8zbmu.streamlit.app/)

*(Note: Replace the link above with the actual URL of your deployed app)*

Deployment is handled automatically by Streamlit Cloud whenever a new commit is pushed to the main branch of the GitHub repository. Secrets (`GOOGLE_API_KEY` and `MAPBOX_API_TOKEN`) are configured directly in the Streamlit Cloud dashboard for security.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

For questions or suggestions, please reach out via GitHub issues or contact the maintainer directly.
