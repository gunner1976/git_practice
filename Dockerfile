FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY casingdesign ./casingdesign
RUN pip install --no-cache-dir ".[web]"
ENV CASINGDESIGN_DB=/data/casingdesign.db
VOLUME ["/data"]
EXPOSE 8000
CMD ["casingdesign", "serve", "--host", "0.0.0.0", "--port", "8000"]
