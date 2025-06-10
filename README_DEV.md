# Development Guide for CrapsSim

This document outlines the necessary steps and configurations to set up your development environment for the CrapsSim project, focusing on local development using Docker for PostgreSQL.

## 1. Environment Variables (.env)

Sensitive information and configuration settings are managed using environment variables, typically stored in a `.env` file at the root of the project.

**Required Environment Variables:**

*   `DB_HOST`: The hostname for the PostgreSQL database. When running PostgreSQL in Docker within Codespaces, this should be the service name of your database container (e.g., `db`).
*   `DB_NAME`: The name of the PostgreSQL database.
*   `DB_USER`: The username for connecting to the PostgreSQL database.
*   `DB_PASSWORD`: The password for the PostgreSQL database user. This should be sourced from a secure secret.

**Example `.env` file:**

```
DB_HOST="db"
DB_NAME="test_crapssim_db"
DB_USER="test_crapssim_user"
DB_PASSWORD="${POSTGRES_PASSWORD}"
```

**Note on `DB_PASSWORD`:**
The `DB_PASSWORD` variable in the example above uses `${POSTGRES_PASSWORD}`. This indicates that the actual password should be provided via a secret management system (e.g., GitHub Codespaces secrets, or your local environment variables) rather than hardcoding it directly in the `.env` file. This is a security best practice.

## 2. Secrets Management

For `DB_PASSWORD` and other sensitive credentials, it is crucial to use a secure method for injecting these values into your environment.

**GitHub Codespaces:**
If you are developing in GitHub Codespaces, you should set `POSTGRES_PASSWORD` as a Codespaces secret. This secret will then be automatically available as an environment variable when your Codespace starts, allowing the `.env` file to correctly resolve `DB_PASSWORD`.

**Local Development:**
For local development outside of Codespaces, you should set the `POSTGRES_PASSWORD` environment variable in your shell before starting your application or Docker Compose. For example:

```bash
export POSTGRES_PASSWORD="your_secure_password_here"
```

## 3. Docker and PostgreSQL Setup

CrapsSim uses Docker to run a PostgreSQL database, ensuring a consistent and isolated development environment.

**`docker-compose.yml`:**
The `docker-compose.yml` file defines the PostgreSQL service. It maps the environment variables from your `.env` file to the PostgreSQL container.

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    container_name: crapssim_postgres_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  db_data:
```

## 4. Getting Started with Development

Follow these steps to set up and start developing:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/crapssim_private.git
    cd crapssim_private
    ```

2.  **Configure Environment Variables:**
    *   Create a `.env` file in the root directory of the project if it doesn't exist.
    *   Ensure `DB_HOST`, `DB_NAME`, `DB_USER` are set as shown in the example `.env` above.
    *   Set the `POSTGRES_PASSWORD` secret in your Codespaces environment or export it locally.

3.  **Start the PostgreSQL Docker Container:**
    Navigate to the project root directory and run:
    ```bash
    docker-compose up -d
    ```
    This command will:
    *   Pull the `postgres:13` Docker image (if not already present).
    *   Create and start a container named `crapssim_postgres_db`.
    *   Map port `5432` from the container to your host machine (or Codespace).
    *   Create a Docker volume `db_data` for persistent storage of your database.

4.  **Verify PostgreSQL Container Status:**
    You can check if the container is running and healthy with:
    ```bash
    docker-compose ps
    ```
    Look for `crapssim_postgres_db` with a `STATUS` of `Up (healthy)`.

5.  **Install Python Dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

You are now ready to start developing on the CrapsSim codebase!