FROM python:3.11-slim

ENV DEBIAN_FRONTEND noninteractive


ENV ACCEPT_EULA=Y
RUN apt-get update -y && apt-get update \
  && apt-get install -y --no-install-recommends curl gcc g++ gnupg unixodbc-dev

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql18 mssql-tools \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

