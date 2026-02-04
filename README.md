# 🚀 Real-Time Crypto Data Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Spark](https://img.shields.io/badge/Apache%20Spark-Streaming-orange)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-3.5-black)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

## 📖 Overview
This project is an end-to-end data engineering pipeline that ingests, processes, and visualizes cryptocurrency trade data in real-time. It connects to the **Binance WebSocket API** to fetch live BTC/USDT trades, buffers them in **Apache Kafka**, processes them using **Spark Structured Streaming**, and stores the results in **PostgreSQL**.

The final output is a low-latency **Streamlit Dashboard** that visualizes price trends using 5-second sliding windows and OHLC (Open-High-Low-Close) aggregation.

## 🏗️ Architecture
The pipeline is fully containerized and runs on a Docker network.

```mermaid
graph LR
    A[Binance WebSocket API] -->|Raw JSON| B(Python Producer)
    B -->|Ingest| C{Apache Kafka}
    C -->|Stream Read| D[Spark Structured Streaming]
    D -->|Micro-batch Processing| E[(PostgreSQL DB)]
    E -->|Query| F[Streamlit Dashboard]
🛠️ Tech Stack
Source: Binance WebSocket API (Asyncio)

Ingestion: Apache Kafka & Zookeeper (Dockerized)

Processing: PySpark (Structured Streaming, Window Functions)

Storage: PostgreSQL (JDBC Sink)

Visualization: Streamlit & Plotly (Real-time autorefresh)

Environment: WSL2 (Ubuntu Linux)

✨ Key Features
Real-Time Aggregation: Spark processes raw tick data into 5-second buckets to calculate average price and volume.

Efficient Storage: Uses PostgreSQL for persistent storage, enabling historical lookback analysis.

Interactive Dashboard: Streamlit UI with uirevision locking to allow zooming while data updates live.

Fault Tolerance: Dockerized Zookeeper manages Kafka brokers; Spark handles late data and failures.

Timezone Handling: Enforced UTC across JVM and Database to prevent timestamps offsets (Asia/Kolkata vs UTC).

🚀 How to Run
1. Prerequisites
Docker & Docker Compose

Python 3.8+

Java 17 (for Spark)

2. Start Infrastructure
Spin up Kafka, Zookeeper, and Postgres:

Bash
docker-compose up -d
3. Setup Environment
Bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
4. Run Pipeline Components
Run these in separate terminals:

Terminal 1: Producer (Ingestion)

Bash
python producer.py
Terminal 2: Spark Processor (ETL)

Bash
python processor.py
Terminal 3: Dashboard (Visualization)

Bash
streamlit run dashboard.py --server.address 0.0.0.0
📊 Dashboard Preview
(Add a screenshot or GIF of your dashboard here)

🔮 Future Improvements
Add Cloud deployment (AWS EC2/EMR).

Implement simple Moving Average (SMA) crossover alerts.

Containerize the Python scripts for a full docker-compose up experience.


***

### **Part 2: The LinkedIn Post**

LinkedIn posts need to be punchy. You want to show that you didn't just "copy code," but that you understand the *architecture*.

**Copy and paste this, but attach a video/GIF of your dashboard moving!**

**Headline:** Building a Real-Time Crypto Streaming Pipeline with Kafka & Spark 🚀

**Body:**
Just wrapped up a new Data Engineering project! I wanted to move beyond batch processing and tackle the challenges of real-time data streams.

I built an end-to-end pipeline that ingests live Bitcoin trades from Binance and visualizes them with sub-second latency.

🛠️ **The Architecture:**
🔹 **Ingestion:** Python Async producer pushing raw ticks to **Apache Kafka**.
🔹 **Processing:** **Apache Spark** (Structured Streaming) reading micro-batches.
🔹 **Transformation:** Spark handles the schema enforcement and time-window aggregation (converting raw ticks into 5-second OHLC buckets).
🔹 **Storage:** Data is written to **PostgreSQL** via JDBC.
🔹 **Viz:** A **Streamlit** dashboard that auto-refreshes to show live market moves.

💡 **Key Engineering Challenge:**
The biggest hurdle was handling the "Timezone Mismatch" between my local machine (Asia/Kolkata), the Docker containers (UTC), and Spark's JVM. I had to enforce UTC across the entire stack to ensure the time-series data aligned perfectly in the dashboard.

💻 **Check out the code & architecture on GitHub:**
[Link to your GitHub Repo]

#DataEngineering #ApacheSpark #Kafka #RealTimeData #Python #Docker #BigData #Streamlit

***

### **Part 3: The "Finishing Touches" Checklist**

1.  **Screenshots:** Take a screenshot of your dashboard (the "dark mode" one you showed me). Save it as `dashboard_screenshot.png` inside your project folder and push it to GitHub. The README code above expects it.
2.  **Requirements.txt:** Don't forget to create this file so others can run your code! Run this command in your terminal:
    ```bash
    pip freeze > requirements.txt
    ```
3.  **Push:**
    ```bash
    git add .
    git commit -m "Final polish for release"
    git push origin main
    ```

You are ready to launch! Good luck with the showcase.
