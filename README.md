# PPRA Contracts Intelligence Dashboard (AI_Project)

A data-driven dashboard built with **Plotly Dash** and **Python**, designed to analyze and visualize procurement contract data using techniques like **Benford’s Law** and **cluster anomaly detection**.  
This tool enables insights into public procurement data by identifying outliers, summarizing key buyer trends, and exploring value distributions.

---

## 📁 Project Structure

│
├── app.py # Main entry point to start the application
├── merged_ppra_data.csv # Primary dataset for analysis
│
├── dashboard/ 				# Core dashboard logic and components
│ ├── pycache/ 				# Auto-generated Python cache files
│ ├── callbacks/ 			# Interactive behavior for dashboard elements
│ ├── layouts/ 				# Page layouts and visualization layouts
│ ├── utils/ 				# Data loading, preprocessing, and initialization scripts
│ │── dash_app.py 			# Initializes and configures the Dash app
│ │── data_loader.py 		# Handles dataset loading and cleaning
│ │── layout_main.py 		# Main layout structure and shared components
│ │── merged_ppra_data.csv 	# Local working copy of dataset
│
├── templates/ 				# HTML templates for Flask integration (if used)
│ └── index.html
│
└── .gitignore 				# Git ignore file for virtualenvs, caches, etc.