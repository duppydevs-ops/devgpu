# GPUaaS (Simulation) — Run Guide

## 1) Clone the project from GitHub

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd <PROJECT_FOLDER>
```

## 2) Open Docker Desktop

Make sure Docker Desktop is running (so Docker Engine is available).

## 3) Start the project with Docker Compose

From the project root (where `docker-compose.yml` is):

```bash
docker-compose up --build -d
```

This will start:

* Django (API + Admin)
* PostgreSQL
* Redis
* Celery Worker
* Celery Beat

## 4) Run database migrations (inside the Django container)

```bash
docker exec -it django-GAAS python manage.py migrate
```

## 5) Create an admin user (superuser)

```bash
docker exec -it django-GAAS python manage.py createsuperuser
```

Follow the prompts to set username/email + password.

## 6) Open Django Admin

Go to:

* `http://localhost:8000/admin/`

Log in using the superuser credentials.

## 7) Use the Admin panel

Inside admin you can manage:

* **GPUs** (create available GPU types and token rates)
* **Jobs** (view user jobs, approve them)
* **Job Logs** (see job lifecycle logs and charging logs)

### Approving jobs

1. Open **Jobs**
2. Select a job and change status to **APPROVED**
3. Save

After approval:

* The **user** can run the job (via the run endpoint).
* Once running, **Celery** will process it and **JobLogs** will appear.

## 8) Useful commands (optional)

### View logs

```bash
docker logs -f django-GAAS
docker logs -f celery_worker-GAAS
docker logs -f redis-GAAS
docker logs -f postgresDB_origin-GAAS
```

### Stop everything

```bash
docker-compose down
```

### Rebuild + restart

```bash
docker-compose down
docker-compose up --build -d
```

## Swagger API Docs

After the containers are running, open Swagger UI here:

* `http://localhost:8000/api/schema/swagger-ui/`

You can use it to test endpoints (list GPUs, create jobs, run/stop jobs, list logs, etc.).
