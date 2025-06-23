# Weather Insights Assistants
This is the weather insights assistant application. This application uses a Large Language Model (GPT 4) 
to answer queries based on weather data sourced from meteostat.com. 

# Features
1. The application is capable of responding to queries related to weather data. The application uses an SQL agent
that generates an appropriate SQL query based on the user prompt, and uses the returned data to augment the LLM's context.
This results in responses that are grounded in the user data. 

2. The left side has the chat interface, with options to send a message, and clear to delete the session. The top-right 
displays a wind-speed and temperature v date time graph. This combined with energy demand data can be used to find correlation
between temp/wind-speed and electricity demand. 

3. Bottom-right displays a basic data summary from the connected SQL database. 

# Architecture
### Data ingestion
Azure Data Factory Pipeline Copy Activity is used to load the weather data from meteostat's hourly endpoint into raw table within a Azure SQL database instance. Following this, unique records are added and columns are mapped within a data-flow operation and loaded into a curated table. 

### SQL Agent 
Azure Open AI GPT 4 is deployed within AI Foundry and used as the base LLM for the SQL agent. This agent is capable of generating SQL queries based off of user prompts, running against the SQL tables, and using the returned data to augment an LLM's capability 
to accurately respond to questions. 

### Backend
The backend runs a containerised FastAPI service on Azure Container Apps. This service exposes 3 endpoints which are as follows: 
| endpoint | method | output  |
|-----------|-------|---------|
| /connect  | GET   | returns database connection status |
| /get_response | POST  | returns LLM agent response  |
| /get_weather data   | POST | returns weather data for visualisation  |

### Frontend
The frontend uses ReactJS, node and Tailwind CSS. It is hosted on Azure App Service (Static Web Apps). 







