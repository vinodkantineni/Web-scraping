# Production Deployment Guide - BiasDigest

This guide outlines step-by-step instructions for building, packaging, and deploying the **BiasDigest SaaS** application to production hosts.

---

## 🛠️ Production Environment Variables
Regardless of the hosting provider, you must configure the following environment variables in your production console:

| Variable | Description | Example / Required Value |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API Credential | *Generate at [AI Studio](https://aistudio.google.com/)* |
| `JWT_SECRET_KEY` | Secret seed string for session hashing | *A long, randomly generated alphanumeric string* |
| `JWT_EXPIRE_MINUTES` | Token validity period in minutes | `1440` (24 hours) |
| `DATABASE_URL` | SQLAlchemy Database Connection URI | `sqlite:///./data/news_bias.db` *(See Persistence note below)* |

> [!CAUTION]
> **Data Persistence Warning**
> SQLite saves data directly to a local file. In containerized clouds (like Render or Cloud Run), container storage is ephemeral and is **reset to empty on every restart/deploy**.
> - **SQLite Solution**: Mount a persistent disk volume to the container (e.g. `/app/data/`) and configure `DATABASE_URL=sqlite:///./data/news_bias.db`.
> - **SaaS Production Solution**: Switch `DATABASE_URL` to a remote managed database URI like PostgreSQL or MySQL (e.g. `postgresql://user:pass@host:5432/db`). SQLAlchemy handles this conversion automatically.

---

## 🐋 Option 1: Local Deployment with Docker

To build and run the unified frontend-backend application locally inside a container:

1. **Build the Container Image**:
   Execute from the project root:
   ```bash
   docker build -t news-bias-digest .
   ```

2. **Run the Container**:
   Pass your local environment secrets:
   ```bash
   docker run -d \
     -p 8000:8000 \
     --env GEMINI_API_KEY="your_gemini_api_key" \
     --env JWT_SECRET_KEY="generate_random_secret_string" \
     --name bias-digest-app \
     news-bias-digest
   ```
   The application will boot and serve the React UI and FastAPI API concurrently on [http://localhost:8000](http://localhost:8000).

3. **Or run with Docker Compose**:
   ```bash
   docker-compose up --build -d
   ```

---

## ☁️ Option 2: Deploy to Render (Web Service)

Render is one of the easiest platforms to deploy containerized single-port web apps.

1. **Create Repository**: Push your code to your private GitHub or GitLab repository.
2. **Create New Web Service**:
   - Log in to [Render](https://render.com/).
   - Click **New +** and select **Web Service**.
   - Connect your GitHub repository.
3. **Configure Settings**:
   - **Name**: `news-bias-digest`
   - **Runtime**: Select **Docker** (Render will automatically detect the root `Dockerfile` and run the multi-stage build).
   - **Region**: Choose a region closest to your users.
   - **Instance Type**: Free tier is sufficient, but 512MB RAM is recommended.
4. **Environment Variables**:
   Under the **Environment** tab, click **Add Environment Variable** and define:
   - `GEMINI_API_KEY` = *(Your Google AI Studio API key)*
   - `JWT_SECRET_KEY` = *(A secure random string)*
5. **Persistent Disk (Optional for SQLite)**:
   If you want to save search history without losing it on deployments:
   - Scroll down to the **Disks** section.
   - Click **Add Disk**.
   - **Name**: `sqlite-data`
   - **Mount Path**: `/app/data`
   - **Size**: `1 GiB`
   - In **Environment Variables**, update `DATABASE_URL` to `sqlite:///./data/news_bias.db`.
6. **Deploy**: Click **Create Web Service**. Render will compile your React assets, build the FastAPI environment, and launch the server.

---

## 🌩️ Option 3: Deploy to Google Cloud Run

GCP Cloud Run provides a serverless platform to run containers at scale.

1. **Build and Upload to Container Registry**:
   Submit a build command to Google Artifact Registry:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/news-bias-digest
   ```

2. **Deploy Container**:
   Deploy the uploaded image directly:
   ```bash
   gcloud run deploy news-bias-digest \
     --image gcr.io/YOUR_PROJECT_ID/news-bias-digest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="JWT_SECRET_KEY=your_secret_key" \
     --set-env-vars="GEMINI_API_KEY=your_gemini_api_key"
   ```

3. **Access Public URL**: Cloud Run will output a public URL (e.g. `https://news-bias-digest-xxxxxx.run.app`) where your SaaS application is live.
