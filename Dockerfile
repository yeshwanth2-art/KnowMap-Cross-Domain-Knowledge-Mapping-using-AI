# Use a Python base image suitable for the libraries
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the required SpaCy model (Crucial for page 04)
# This prevents the [E050] error during container startup
RUN python -m spacy download en_core_web_sm

# Copy the entire application structure (app.py and the pages folder)
COPY app.py $APP_HOME/
COPY pages/ $APP_HOME/pages/

# Expose the default Streamlit port
EXPOSE 8501

# Define the command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]