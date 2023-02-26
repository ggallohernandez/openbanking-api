FROM python:3.11.2-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the rest of the application code into the container
COPY . .

# Run the equivalent to dpkg-reconfigure locales
RUN apt update && apt -y install locales
RUN locale-gen --purge es_UY.UTF-8
RUN echo -e 'LANG="es_UY.UTF-8"\nLANGUAGE="es_UY:es"\n' > /etc/default/locale

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install && playwright install-deps

# Expose the port that Scrapy will run on
EXPOSE 6800

# Start the Scrapy project using the scrapyd service
CMD ["scrapyd"]