# Weather Insight Assistant
This is the weather insights assistant application. This application uses a Large Language Model (GPT 4) 
to answer queries based on weather data sourced from meteostat.com.  
URL: https://black-ground-088a26003.6.azurestaticapps.net/ 

# Features
1. QA Layer on structured data. 
2. Weather trends visualisation. 
3. Live Data summary.

# Architecture

Source data is ingested from meteostat.com /hourly endpoint with a Azure Data Factory pipeline and stored in a Azure SQL Database table. This pipeline is scheduled to run hourly to load the most recent weather data available. Currently, the app uses weather data from London, UK.  

### Backend
The backend runs a containerised FastAPI service on Azure Container Apps. This service exposes 3 endpoints which are as follows: 
| endpoint | method | output  |
|-----------|-------|---------|
| /connect  | GET   | returns database connection status |
| /get_response | POST  | returns LLM agent response  |
| /get_weather data   | POST | returns weather data for visualisation  |

### Frontend
The frontend uses React, Node and Tailwind CSS. It is hosted on Azure App Service (Static Web Apps). 

# Enhancements

1. Consume energy demand data corresponding to weather data and create visualisations. 
2. Add feature to create, manage and store user specific data and information.
3. Improvements to UI (including using a framework like Vite or NextJS). 
4. Build analytics on Microsoft Fabric data warehouse. 
5. Provide support for more locations based on user requirements.
6. Add connectors for multiple data sources so users can upload / provide their own data sources to trigger the end to end pipeline.

# Local Setup

1. Clone the backend service from [here](https://github.com/sammyamajumdar/weather-insight-assistant-backend.git)
2. Clone the frontend service from [here](https://github.com/sammyamajumdar/weather-insight-assistant-frontend.git) 
3. Create virtual environment and run pip install -r requirements.txt
4. Generate required environment variables from the .env.template file and populate the .env file (Deploy and configure Azure services from next section)
5. Run python -m fastapi run main.py from the backend service directory (API endpoints will be exposed in port 8000)
6. Run npm install from the frontend service directory
7. Run npm run start from the terminal

# Azure setup
Required Services: Azure Foundry AI, Azure SQL Database, Azure Data Factory, Azure Container Apps, Azure App Services

# Next Steps
1. Terraform module
2. CI/CD pipeline
3. React Jest Tests
4. Power BI report





