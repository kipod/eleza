FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m pip install --upgrade pip

COPY . .

# tell the port number the container should expose
EXPOSE 5005

CMD [ "python", "-m", "flask", "run",  "-h", "0.0.0.0", "-p", "5005" ]
