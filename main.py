from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from sqlalchemy.engine import create_engine
from urllib.parse import quote_plus
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import AzureChatOpenAI

def database_connector(database_connection_string, database_password, schema="dbo"): 
    try: 
        db_engine = create_engine(database_connection_string % quote_plus(database_password))
        db = SQLDatabase(db_engine, view_support=True, schema=schema)
        print(db.dialect)
        print(db.get_usable_table_names())
        db.run("select convert(varchar(25), getdate(), 120)")
        
        return db
    except Exception as e: 
        print(f"Connection to database failed. {e}")


def get_llm_client(model_name = "gpt-4", deployment = "gpt-4"): 

    azurellm = AzureChatOpenAI(
        model_name=model_name,
        deployment_name=deployment 
    )

    return azurellm

def get_sql_agent(azurellm, database):
    toolkit = SQLDatabaseToolkit(db=database, llm=azurellm)

    agent_executor = create_sql_agent(
        llm=azurellm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True
    )

    return agent_executor

base_prompt = """You are a helpful assistant working for a energy supplier. They are keen to understand their demand forcasts to efficiently plan their operations. 
Based on the data provided, you will respond to any questions that an user might have.
For every user question which will be provided below, please return an analysis and an explanation for your analysis. 
Please dont use pleasantries of any form. Do not hallucinate, if the response is not within the data or you cannot figure it, 
return information not found."""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)


class DBConnectRequest(BaseModel):
    database_connection_string: str
    database_password: str
    schema: Optional[str] = None

class QueryRequest(BaseModel):
    query: str


load_dotenv()

azure_openai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
azure_api_version = os.environ["OPENAI_API_VERSION"]

database_connection_string = os.environ["SQL_DATABASE_CONNECTION_STRING"]
database_password = os.environ["SQL_DATABASE_PASSWORD"]

@app.get("/connect")
def create_database_connection(): 
    try: 
        db = database_connector(database_connection_string, database_password, schema="dbo")
        return {"status": "connected"}
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/get_response")
def get_llm_response(query: QueryRequest): 
    try: 
        db = database_connector(database_connection_string, database_password, schema="dbo")
        azurellm = get_llm_client()
        llm_agent = get_sql_agent(azurellm, db)
        llm_response = llm_agent.invoke(base_prompt + query.query)
        return {"response": llm_response}
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/weather_data")
def get_data(
    start_datetime: datetime = Query(..., description="Start datetime (YYYY-MM-DD HH:MM:SS)"),
    end_datetime: datetime = Query(..., description="End datetime (YYYY-MM-DD HH:MM:SS)"),
    schema: str = Query("dbo", description="Database schema")
):
    try:
        
        db_engine = create_engine(database_connection_string % quote_plus(database_password))
        with db_engine.connect() as conn:
            query = text(f"""
                SELECT temperature, wind_speed, sun_shine, time
                FROM [{schema}].[curated_weather_data]
                WHERE time >= :start_datetime AND time <= :end_datetime
                ORDER BY time
            """)
            result = conn.execute(query, {
                "start_datetime": start_datetime,
                "end_datetime": end_datetime
            })

            columns = ["temperature", "wind_speed", "sun_shine", "time"]
            data = [dict(zip(columns, row)) for row in result.fetchall()]

        return {"data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
