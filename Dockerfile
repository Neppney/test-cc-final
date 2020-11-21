# set base image (host os)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local directoy to the working directory
COPY / .

EXPOSE 8080
# command to run on container start
CMD [ "python", "./app.py" ]
