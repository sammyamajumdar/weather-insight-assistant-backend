"""
This script contains the backend service APIs for the weather insight assistant application.
"""
import os
import re
from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_core.exceptions import OutputParserException
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError


def database_connector(connection_string, db_password, schema="dbo"):
    """
    Establishes a connection to a SQL database and returns a SQLDatabase object.

    Args:
        connection_string (str): The SQLAlchemy connection string 
            with a placeholder for the password.
        db_password (str): The database password to be securely 
            inserted into the connection string.
        schema (str, optional): The database schema to use. Defaults to "dbo".

    Returns:
        SQLDatabase: An instance of the SQLDatabase class connected to the specified database.

    Raises:
        OperationalError: If the connection to the database fails.

    Example:
        db = database_connector("mssql+pyodbc://user:%s@server 
        /db?driver=ODBC+Driver+17+for+SQL+Server", "mypassword")
    """
    try:
        db_engine = create_engine(connection_string % quote_plus(db_password))
        db = SQLDatabase(db_engine, view_support=True, schema=schema)
        print(db.dialect)
        print(db.get_usable_table_names())
        db.run("select convert(varchar(25), getdate(), 120)")
        return db
    except OperationalError as e:
        print(f"Connection to database failed. {e}")


def get_llm_client(model_name = "gpt-4", deployment = "gpt-4"):
    """
    Creates and returns an AzureChatOpenAI client for interacting with Azure OpenAI chat models.

    Args:
        model_name (str, optional): The name of the OpenAI model to
            use (e.g., "gpt-4"). Defaults to "gpt-4".
        deployment (str, optional): The deployment name 
            configured in Azure OpenAI. Defaults to "gpt-4".

    Returns:
        AzureChatOpenAI: An instance of the AzureChatOpenAI 
        client configured with the specified model and deployment.

    Example:
        llm_client = get_llm_client(model_name="gpt-4", deployment="gpt-4")
    """

    azurellm = AzureChatOpenAI(
        model_name=model_name,
        deployment_name=deployment
    )

    return azurellm

def get_sql_agent(azurellm, database):
    """
    Creates and returns a SQL agent executor for interacting with a database using a language model.

    Args:
        azurellm (AzureChatOpenAI): An initialized Azure OpenAI language model client.
        database (SQLDatabase): An instance of SQLDatabase connected to the target database.

    Returns:
        AgentExecutor: A configured SQL agent executor that can 
            process natural language queries against Azure SQL db.

    Example:
        agent = get_sql_agent(azurellm, database)
        response = agent.invoke({"input": "Show me all users who signed up this month."})
    """
    toolkit = SQLDatabaseToolkit(db=database, llm=azurellm)

    agent_executor = create_sql_agent(
        llm=azurellm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True
    )

    return agent_executor

BASE_PROMPT = """You are a helpful assistant working for a energy supplier.
They are keen to understand their demand forcasts to efficiently plan their operations.
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
    """
    Data model for a database connection request.

    This model is used to encapsulate the parameters required to establish a connection
    to a database, including the connection string, password, and optional schema.

    Attributes:
        database_connection_string (str): The database connection string, typically 
        including driver, host, and credentials (except password).
        database_password (str): The password for authenticating with the database.
        schema (Optional[str]): The database schema to use. If not provided, 
        the default schema will be used.
    """
    database_connection_string: str
    database_password: str
    schema: Optional[str] = None

class QueryRequest(BaseModel):
    """
    Data model for submitting a request to the LLM agent.

    Attributes:
        query (str): query string to be sent to the LLM agent.
    """
    query: str


load_dotenv()

azure_openai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
azure_api_version = os.environ["OPENAI_API_VERSION"]

database_connection_string = os.environ["SQL_DATABASE_CONNECTION_STRING"]
database_password = os.environ["SQL_DATABASE_PASSWORD"]

@app.get("/connect")
def create_database_connection():
    """
    Attempts to establish a connection to the database using provided credentials.

        Returns:
        dict: A dictionary indicating the connection status, e.g., {"status": "connected"}.

    Raises:
        HTTPException: If the connection to the database fails, 
        an HTTPException with status code 500 is raised."""
    try:
        database_connector(database_connection_string, database_password, schema="dbo")
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/get_response")
def get_llm_response(query: QueryRequest):
    """
    Processes a SQL query request using a SQL LLM agent and returns the response.
    Args:
        query (QueryRequest): The request object containing the query string to be processed.

    Returns:
        dict: A dictionary with the key "response" containing 
        either the agent's response or the raw output
              in case of a parsing error.

    Raises:
        HTTPException: If a general error occurs during processing, 
        an HTTPException with status code 500 is raised.
    """
    try:
        db = database_connector(database_connection_string, database_password, schema="dbo")
        azurellm = get_llm_client()
        llm_agent = get_sql_agent(azurellm, db)
        try:
            llm_response = llm_agent.invoke(BASE_PROMPT + query.query)
            return {"response": llm_response}
        except OutputParserException as e:
            raw_output = None
            for attr in ["output", "response", "llm_output", "text"]:
                if hasattr(e, attr):
                    raw_output = getattr(e, attr)
                    break
            if raw_output is None:
                match = re.search(r"Could not parse LLM output:\s*`(.+?)`", str(e), re.DOTALL)
                if match:
                    raw_output = match.group(1)
                else:
                    raw_output = str(e)
            return {"response": raw_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

class WeatherDataRequest(BaseModel):
    """
    Data model for requesting weather data within a specific datetime range.

    Attributes:
        start_datetime (datetime): The start of the datetime range for the weather data query.
        end_datetime (datetime): The end of the datetime range for the weather data query.
        schema (str): The database schema to use for the query. Defaults to "dbo".
    """
    start_datetime: datetime
    end_datetime: datetime
    schema: str = "dbo"

@app.post("/weather_data")
def get_data(request: WeatherDataRequest):
    """
    Retrieves weather data records from the database for a specified datetime range.

    Args:
        request (WeatherDataRequest): The request object containing the start and end datetimes
                                      for the data query and the database schema to use.

    Returns:
        dict: A dictionary with the key "data" containing a list of weather data records,
              where each record is represented as a dictionary with keys:
              "temperature", "wind_speed", "sun_shine", and "time".

    Raises:
        HTTPException: If an error occurs during the database connection or query execution,
                       an HTTPException with status code 500 and error details is raised.

    Example:
        >>> req = WeatherDataRequest(
        ...     start_datetime=datetime(2024, 1, 1, 0, 0),
        ...     end_datetime=datetime(2024, 1, 2, 0, 0)
        ... )
        >>> get_data(req)
        {'data': [
            {'temperature': 23, 'wind_speed': 5, 'sun_shine': 8, 
            'time': datetime(2024, 1, 1, 12, 0)},
            ...
        ]}
    """
    try:
        db_engine = create_engine(database_connection_string % quote_plus(database_password))
        with db_engine.connect() as conn:
            query = text(f"""
                SELECT temperature, wind_speed, sun_shine, time
                FROM [{request.schema}].[curated_weather_data]
                WHERE time >= :start_datetime AND time <= :end_datetime
                ORDER BY time
            """)
            result = conn.execute(query, {
                "start_datetime": request.start_datetime,
                "end_datetime": request.end_datetime
            })

            columns = ["temperature", "wind_speed", "sun_shine", "time"]
            data = [dict(zip(columns, row)) for row in result.fetchall()]

        return {"data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
