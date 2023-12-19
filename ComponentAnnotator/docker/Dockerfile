# Use the official Python image as a base image
FROM python:3.10 as python-base

# Set the working directory in the container
RUN mkdir component-annotator
WORKDIR /component-annotator
COPY pyproject.toml /component-annotator
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -n --no-ansi  --without dev
# Copy the entire project code to the container
COPY . .
# Set the environment variable PYTHONPATH to include the source folder
ENV PYTHONPATH=/component-annotator/src

# (Maybe do this somewhere else later)
# Make sure that scripts have execute permission
RUN chmod +x /component-annotator/src/arcan/arcan.sh
RUN chmod +x /component-annotator/src/arcan/run-arcan.sh

# Ensure Java is here
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* # && \
    # rm -rf /var/cache/oracle-jdk17-installer;

EXPOSE 8669
HEALTHCHECK CMD curl --fail http://localhost:8669/_stcore/health

# Specify the command to run on container start
CMD ["python", "src/main.py"]
