FROM python:3.12-slim
WORKDIR /opt/pdfstudio
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir . && useradd -r -u 10001 pdfstudio
USER pdfstudio
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
