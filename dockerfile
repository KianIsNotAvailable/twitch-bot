FROM python:3.8
WORKDIR /usr/src/app
COPY . .
##install dependancies
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "slots.py"]