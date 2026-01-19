FROM python:3.10-bookworm

WORKDIR /usr/src

RUN apt-get update && apt-get install -y libreoffice --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN pip install PyMuPDF python-docx openpyxl python-pptx requests
