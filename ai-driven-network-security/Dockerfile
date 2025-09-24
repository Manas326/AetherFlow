FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=src/web/app.py
EXPOSE 5000
CMD ["python", "src/web/app.py"]
