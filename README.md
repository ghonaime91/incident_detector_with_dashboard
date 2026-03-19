# 🚨 Incident Detector with Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

An integrated system designed for real-time incident detection and processing, featuring an interactive dashboard for data visualization, reporting, and analytics.

---

## 📌 Project Overview
This project provides a technical solution for automating incident monitoring and logging. It features a Graphical User Interface (GUI) for administrators to track various cases, analyze incident frequency, and make data-driven decisions through live visual indicators.

## ✨ Key Features
* **Real-time Monitoring:** Instant data updates as incidents occur.
* **Interactive Dashboard:** Visual interface with precise statistics and dynamic charts.
* **Data Management:** Detailed logging including timestamps, types, severity, and status.
* **Responsive UI:** Modern design compatible with desktops, tablets, and mobile devices.
* **Efficient Filtering:** Built-in search and filtering for quick access to specific records.

## 🛠 Tech Stack
* **Backend:** Python with **Flask** Framework.
* **Frontend:** HTML5, CSS3 (Bootstrap), JavaScript.
* **Visualization:** Chart.js / D3.js for data representation.
* **Database:** SQLite / MySQL for structured data storage.

## 🚀 Quick Setup & Execution
Copy and paste the following block into your terminal to clone, set up the environment, and run the project immediately:

```bash
# Clone the repository
git clone [https://github.com/ghonaime91/incident_detector_with_dashboard.git](https://github.com/ghonaime91/incident_detector_with_dashboard.git)
cd incident_detector_with_dashboard

# Create and activate virtual environment
# For Windows:
python -m venv venv && .\venv\Scripts\activate
# For Linux/Mac:
# python3 -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
