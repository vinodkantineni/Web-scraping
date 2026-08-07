# BiasDigest: AI News Bias Detection & Debiasing System
> Combat information overload, isolate media slants, and generate objective, fact-based news coverage instantly.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/react-18-cyan?style=for-the-badge&logo=react)

### 🟢 [Live Demo: Try it here!](https://news-bias-digest.onrender.com/)

## 📸 Visual Preview
<img width="1919" height="900" alt="image" src="https://github.com/user-attachments/assets/a160f09f-2b9e-4654-beae-a177d88b6332" />


### Analysis Input
<img width="1101" height="570" alt="image" src="https://github.com/user-attachments/assets/6c574233-cfe9-41c6-b57e-a1b5d7e43d44" />


### Bias Detection Results & Chart
<img width="1001" height="727" alt="image" src="https://github.com/user-attachments/assets/cdb03c5a-8cb9-4c33-9aba-163b66680101" />
<img width="968" height="471" alt="image" src="https://github.com/user-attachments/assets/74bc81ce-2f2a-4910-a301-e374f7bdc28c" />



## ✨ Features
* **Interactive Dashboard**: Paste an article URL or raw text to instantly analyze news content.
* **Political Bias Spectrum**: Accurately classifies left, center, and right leanings using AI and visualizes it via dynamic charts.
* **Objective Summarization**: Condenses long-winded articles into quick 100-130 word fact-based summaries.
* **Neutral Debiasing Engine**: Automatically strips emotional language and political framing to rewrite the news in a purely neutral tone.
* **Bias Reduction Metric**: Calculates the exact percentage of bias successfully removed from the original text.
* **History Tracking**: Secure JWT authentication paired with a SQLite database automatically saves your past analyses.

## 🛠️ Tech Stack
* **Frontend**: React (Vite), React Router, Lucide Icons, Chart.js, Glassmorphism CSS.
* **Backend**: FastAPI, SQLAlchemy (SQLite), JWT Authentication, `newspaper3k`.
* **AI Engine**: Google Gemini API (`gemini-1.5-flash`) for lightning-fast inference.
* **Infrastructure**: Docker, Docker Compose (Deployable on 512MB Free Tiers).

## 🚀 Installation

### Prerequisites
* Python 3.11+
* Node.js 18+
* A [Google Gemini API Key](https://aistudio.google.com/)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/bias-digest.git
cd bias-digest
```

### 2. Configure Environment Variables
Create a `.env` file inside the `backend/` directory:
```env
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=generate_a_secure_random_string_here
JWT_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./news_bias.db
```

### 3. Install Dependencies
```bash
# Setup Python Backend
python -m venv .venv

# Windows
.\.venv\Scripts\pip install -r backend/requirements.txt
# macOS/Linux
.venv/bin/pip install -r backend/requirements.txt

# Setup React Frontend
cd frontend
npm install
cd ..
```

## 💻 Usage Examples

### Running the App Locally
Start both the FastAPI backend and Vite frontend concurrently using the root launcher script:

```bash
# Windows
.\.venv\Scripts\python run.py

# macOS/Linux
.venv/bin/python run.py
```

* **Web UI**: Access the dashboard at [http://localhost:5173](http://localhost:5173)
* **API Docs**: Access the Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Running via Docker
If you prefer to run the entire stack inside a container:
```bash
docker-compose up --build -d
```

## 🤝 Contributing Guide
We welcome contributions to make BiasDigest even better! 
1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

*(See our [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) for more detailed guidelines if applicable).*

## 📄 License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.
