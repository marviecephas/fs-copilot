# 🏎️ Formula Student Co-Pilot (FS-AI)

**Your AI Race Engineer, optimized for precision and speed.**

![Status](https://img.shields.io/badge/Status-Beta-orange)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Engine](https://img.shields.io/badge/Search-Optimized%20RAG-red)

## 📖 Evolution of the Project

**Formula Student Co-Pilot** has transitioned from a basic multi-agent setup to a high-performance **Retrieval-Augmented Generation (RAG)** system. It is designed to help FSAE/FS teams navigate complex technical regulations (like the 180+ page rulebook) without the latency or "hallucination" issues common in standard LLMs.

The system now features **"Sweet Spot" Retrieval**, balancing context depth with API latency to ensure engineers get accurate, cited rules (like the 60° Tilt Test or Restrictor placement) within the 15-second WhatsApp timeout.

## ⚙️ Optimized Architecture

The system utilizes a **Shotgun Search & Full-Page Retrieval** pattern to ensure no technical details are missed at the bottom of pages:



### 🧠 The "Sweet Spot" Logic
* **Context Window**: The system retrieves the top 6 most relevant rule sections to maximize accuracy.
* **Density**: Each snippet provides ~3000 characters of text to ensure rules at the bottom of pages (like CV 1.7.2) are fully visible to the AI.
* **Latency Control**: Optimized to process results and respond within the Twilio 15-second window to prevent connection timeouts.

## ✨ Enhanced Features

* **🛡️ Security Hardened**: Environment variables are strictly managed via Secrets to prevent API leaks and unauthorized access.
* **📏 Technical Precision**: Specialized in identifying complex sequences, such as:
    * **Naturally Aspirated**: Air flows through the Throttle Body, then the Restrictor.
    * **Forced Induction**: The Restrictor is placed upstream of the Compressor and Throttle Body.
* **🧪 Scrutineering Ready**: Detailed knowledge of the tilt test, including the 60° angle and zero-leakage requirements.



## 🛠️ Tech Stack

* **LLM**: Google Gemini 2.5 Flash Lite (Optimized for speed and context).
* **Framework**: FastAPI with Google Agent Development Kit (ADK).
* **Storage**: JSON Vectorized Rules Database.
* **Deployment**: Render (24/7 Web Service).

## 🚀 Deployment (Production)

### 1. Environment Variables
Ensure the following are set in your deployment environment (Never in `main.py`!):
* `GOOGLE_API_KEY`: Fresh key from Google AI Studio.
* `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN`: From your Twilio Console.

### 2. Manual Deployment (Render)
1.  Connect this GitHub Repo to **Render**.
2.  Set Build Command: `pip install -r requirements.txt`.
3.  Set Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`.
4.  Update Twilio Webhook to your new Render URL.

## 📸 Real-World Interaction

> **User**: "What is the sequence for a turbocharger restrictor?"
>
> **FS Co-Pilot**: "Checking Rule CV 1.7.2... For turbocharged engines, the **restrictor must be upstream** of the compressor and the throttle body. 
> **Correct Sequence**: Air Intake → 20mm Restrictor → Compressor → Throttle Body → Engine."

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss proposed changes.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
