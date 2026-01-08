# 1. Base Image: Use a lightweight Python version (Linux based)
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy files from your PC to the Container
# We copy requirements first to leverage Docker caching
COPY requirements.txt .

# 4. Install dependencies
# We install system libraries (libgomp1) needed for LightGBM
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your app code
COPY . .

# 6. Expose the port Streamlit runs on
EXPOSE 8501

# 7. The Command to run the app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]