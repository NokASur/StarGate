FROM python:3.13

LABEL authors="NokSyte"

RUN mkdir /StarGate
WORKDIR /StarGate

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/StarGate:/StarGate/Server:${PYTHONPATH}"

RUN pip install --upgrade pip

COPY Server/req.txt .

RUN pip install -r ./req.txt

COPY . .

CMD ["python", "Server/main.py"]