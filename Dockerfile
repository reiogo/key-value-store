FROM python:3.11-slim

WORKDIR /usr/key-value

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

#CMD ["python", "./src/app.py"]
CMD ["bash"]
