FROM python:3.10-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# default command runs the scraper; override in production if needed
CMD ["python", "scraper/scraper.py"]
