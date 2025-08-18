### Collector 
A full-stack web application made for the course Artificial Intelligence for collecting and analyzing data, built with a modern Python backend and containerized for easy deployment and development.

Backend: FastAPI

Frontend: Streamlit

Database: PostgreSQL

Containerized: Using Docker and Docker Compose

Quick Setup:
1. Clone this repository

    git clone https://github.com/andrejwastaken/collector.git

    cd collector

2. Set up environment variables

    Create a .env file in the project root by copying the template.
    This file manages all your secrets and configurations.
    ## .env
    POSTGRES_DB=X

    POSTGRES_USER=X

    POSTGRES_PASSWORD=X

    POSTGRES_HOST=db

    POSTGRES_PORT=5432
   
    cp .env.example .env

   Now, edit the .env file with your desired database credentials


3. Build and run the project using Docker Compose
This command will build the Docker images and start all services. Make sure you have Docker and Docker Compose installed on your system.

    docker compose up --build -d

    The backend of the application will be available at http://localhost:8000, and the interactive API documentation will be at http://localhost:8000/docs.

4. Apply database migrations
    Run the following commands to create the database tables based on your SQLAlchemy models.

    Generate the initial migration script (only needed the first time):

    docker compose exec backend alembic revision --autogenerate -m "Initial database schema"

    Apply the migrations to the database:

    docker compose exec backend alembic upgrade head

5. Populate the database (Optional)
    If you have a seeding script to load initial data into the database (e.g., in scripts/seed.py), run it with the following command:

    docker compose exec backend python scripts/seed.py

Note:

Anytime you change your SQLAlchemy models in backend/app/models.py, you must generate a new migration (Step 4.1) and apply it (Step 4.2).

If you run into any issues, feel free to open an issue.
