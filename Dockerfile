FROM python:3.11.2-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the rest of the application code into the container
COPY . .

# Configure timezone and locale
ENV LANG=es_UY.UTF-8
RUN echo "America/Montevideo" > /etc/timezone
RUN apt update && apt -y install locales && \
    sed -i -e "s/# $LANG.*/$LANG UTF-8/" /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=$LANG

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium && playwright install-deps

# Expose the port that Scrapy will run on
EXPOSE 6800

# Start the Scrapy project using the scrapyd service
CMD ["scrapyd"]