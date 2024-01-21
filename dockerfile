FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000 || exit 1

CMD ["python", "slots.py"]
