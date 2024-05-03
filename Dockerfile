#
FROM python:3.12

#
WORKDIR /code

#
COPY requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY app /code/app

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]


## Use the official Python image as the base image
#FROM python:3.12 as requirements-stage
#
## Set the working directory in the container
#WORKDIR /tmp
#
## Install Poetry
#RUN pip install poetry
#
## Copy the dependency files to the working directory
#COPY pyproject.toml ./poetry.lock* /tmp/
#
## Export the dependencies to a requirements.txt file
#RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
#
## Use a new Python image as the base image
#FROM python:3.9
#
## Set the working directory in the container
#WORKDIR /code
#
## Copy the requirements.txt file from the requirements stage to the working directory
#COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
#
## Install the dependencies
#RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
#
## Copy the application code to the working directory
#COPY app /code/app
#
## Set the default command to run the application
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

