# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver using the latest stable version approach
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
    && echo "Chrome major version: $CHROME_VERSION" \
    && if [ "$CHROME_VERSION" -ge 115 ]; then \
        # For Chrome 115+, use Chrome for Testing approach
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") \
        && echo "Using Chrome for Testing ChromeDriver version: $CHROMEDRIVER_VERSION" \
        && wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
        && unzip /tmp/chromedriver.zip -d /tmp/ \
        && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    else \
        # Fallback for older Chrome versions
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") \
        && echo "Using legacy ChromeDriver version: $CHROMEDRIVER_VERSION" \
        && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
        && unzip /tmp/chromedriver.zip -d /tmp/ \
        && mv /tmp/chromedriver /usr/local/bin/chromedriver; \
    fi \
    && chmod +x /usr/local/bin/chromedriver \
    && chromedriver --version \
    && rm -rf /tmp/chromedriver* /tmp/chrome*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY README.md .

# Create output directory
RUN mkdir -p output

# Create Chrome startup script to handle cleanup
RUN echo '#!/bin/bash\n\
# Clean up any existing Chrome processes and temp directories\n\
pkill -f chrome || true\n\
rm -rf /tmp/.org.chromium.* /tmp/chrome-* /tmp/.chrome-* || true\n\
mkdir -p /tmp/chrome-data\n\
chmod 755 /tmp/chrome-data\n\
\n\
# Start the Python application\n\
exec "$@"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set environment variables for headless operation
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Expose port for health checks (optional)
EXPOSE 8080

# Create a non-root user for security
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - run in continuous mode with headless
CMD ["python", "src/production_scraper.py", "--continuous", "--headless", "--max-items", "0", "--max-scrolls", "400", "--scan-interval", "300"]
