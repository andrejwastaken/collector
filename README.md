Collector 🚗
============

An AI-powered search and analysis application for car data, built for the "Artificial Intelligence" course.

Overview
-----------

Collector is a full-stack web application designed to demonstrate the principles of data collection and analysis using AI. This project uses a modern Python stack, containerized with Docker for easy setup and deployment. The core functionality is built around a Retrieval-Augmented Generation (RAG) pipeline: user queries are converted into vector embeddings to find relevant car data from a ChromaDB vector store, and the results are passed to an Ollama-hosted LLM to generate a natural language response.

Features
----------

*   **Semantic Search**: Ask questions in natural language (e.g., "What are the cheapest cars in Skopje?") to find relevant information.
    
*   **Interactive Frontend**: A simple and clean user interface built with Streamlit.
    
*   **Robust Backend**: A scalable and documented API powered by FastAPI.
    
*   **Persistent Data Storage**: Uses PostgreSQL for structured data and ChromaDB for vector embeddings.
    
*   **Containerized Environment**: Fully self-contained with Docker and Docker Compose for a one-command setup.
    
*   **Database Migrations**: Schema changes are managed gracefully with Alembic.
    

Tech Stack
--------------

| Component       | Technology |
|-----------------|------------|
| **Backend**     | [FastAPI](https://fastapi.tiangolo.com/), [Python 3.12](https://www.python.org/) |
| **Frontend**    | [Streamlit](https://streamlit.io/) |
| **Database**    | [PostgreSQL](https://www.postgresql.org/) |
| **Vector Store**| [ChromaDB](https://www.trychroma.com/) |
| **LLM/Embeddings** | [Ollama](https://ollama.com/) |
| **Containerization** | [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) |
| **Migrations**  | [Alembic](https://alembic.sqlalchemy.org/) |


Getting Started
------------------

Follow these steps to get the project up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed and running on your host machine:

*   [**Docker**](https://docs.docker.com/get-docker/) **&** [**Docker Compose**](https://docs.docker.com/compose/install/): For running the containerized services.
    
*   [**Ollama**](https://ollama.com/): This project requires Ollama for serving the LLM and embedding models locally.
    
    *   ollama is configured to pull the necesary models in start.sh.
        
    *   **Important**: Ensure the Ollama desktop application or background service is running before you proceed to the next steps.
        

### 1\. Scrape Data for PostgreSQL

The application requires a dataset to function. You must first run the scraping scripts (located in backend/scripts) to generate the data (e.g., into a .csv file) that will be loaded into the PostgreSQL database. For ease of use, running the cars_etl script is prefered as it does the whole process automatically (scrape -> clean -> insert into database), but for that you will need to have completed step 5 (initialized Postgres). 

_(Note: This is a manual step. You need to execute your data scraping process first and place the output where the application can find it.)_

### 2\. Clone the Repository
```bash
git clone [https://github.com/andrejwastaken/collector.git](https://github.com/andrejwastaken/collector.git)
cd collector
```

### 3\. Configure Environment Variables

Create a .env file from the following example template. This file will hold your database credentials. 
```
# .env.example
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=5432
```
```
cp .env.example .env   `
```
Now, open the newly created .env file and customize the variables (according to docker compose) if needed. 

### 4\. Build and Run with Docker Compose

This single command will build the Docker images, create the necessary containers, and start all services in detached mode (-d).

```
docker compose up --build -d   `
```

### 5\. Apply Database Migrations

Once the containers are running, you need to create the database tables using Alembic.

First, **generate an initial migration script** (you only need to do this the very first time):

```
docker compose exec backend alembic revision --autogenerate -m "Initial database schema"   `
```

Next, **apply the migration** to the database to create the tables:

```
docker compose exec backend alembic upgrade head   `
```

> **Note**: Anytime you change your SQLAlchemy models in backend/app/models.py, you must generate and apply a new migration to update the database schema.

### 6\. Populate Databases (PostgreSQL & ChromaDB)

For Postgres, if you have already ran the scrape and clean scripts, you can now run insert_to_db or run the cars_etl script as mentioned in step 1. 
```
docker compose exec backend python -m scripts.cars_etl  
```

To populate the ChromaDB vector store with embeddings for semantic search, run the following script. The vector database is configured to store the embeddings locally.

Run the backfill script inside the running backend container to embed your data from Postgres into ChromaDB:

```  
docker compose exec backend python -m app/backfill_runner`
```

This script will read the stored data you scraped in Step 1 and populate ChromaDB with the necessary embeddings.

Usage
---------

Once all the services are running and the databases are populated, you can access the application:

*   **Frontend Application**: Open your browser and go to http://localhost:8501
    
*   **Backend API Docs**: The interactive Swagger/OpenAPI docs are available at http://localhost:8000/docs