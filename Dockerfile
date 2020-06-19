# Base container
FROM python:3.6
# Add requirements, code
COPY src/requirements.txt /
RUN pip install -r requirements.txt
COPY src/ /
# Declare and expose service listening port
EXPOSE 5566/tcp
# Declare entrypoint of that exposed service
ENTRYPOINT ["python3", "./web_main.py"]

#Env variable for Email Address and password
ENV EMAIL_ADRESS="testmami46@gmail.com" \
    EMAIL_PASSWORD="ogovnooorodzsjol"
