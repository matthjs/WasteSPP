# Use the official Python image as a base image
FROM python:3.10 as python-base

# Set the working directory in the container
RUN mkdir componentannotator
WORKDIR /componentannotator
COPY pyproject.toml /componentannotator
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -n --no-ansi  --without dev
# Copy the entire project code to the container
COPY . .
# Set the environment variable PYTHONPATH to include the source folder
ENV PYTHONPATH=/componentannotator/src

EXPOSE 8669
HEALTHCHECK CMD curl --fail http://localhost:8669/_stcore/health

# Specify the command to run on container start
CMD ["python", "src/main.py"]
