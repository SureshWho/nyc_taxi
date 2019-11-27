# The Dockerfile defines the image's environment
# Import Python runtime and set up working directory
FROM python:3.7.4-buster
WORKDIR /app
ADD . /app

ENV GOOGLE_APPLICATION_CREDENTIALS /app/prj-nyc-taxis-9877814e83d5.json 

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Open port 8080 for serving the webpage
EXPOSE 90

# Run app.py when the container launches
CMD ["python", "app.py"]
