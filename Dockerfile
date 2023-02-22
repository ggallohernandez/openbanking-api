FROM python:3.11.2-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the rest of the application code into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for the Scrapy settings module
ENV SCRAPY_SETTINGS_MODULE=openbanking.settings

# Expose the port that Scrapy will run on
EXPOSE 6800

# Start the Scrapy project using the scrapyd service
CMD ["scrapyd"]