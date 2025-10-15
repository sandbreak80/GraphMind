.PHONY: build up down logs restart ingest stats clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

ingest:
	curl -X POST http://localhost:8000/ingest \
		-H "Content-Type: application/json" \
		-d '{"force_reindex": false}'

stats:
	curl -s http://localhost:8000/stats | jq

health:
	curl -s http://localhost:8000/ | jq

clean:
	docker-compose down -v
	rm -rf outputs/*
	rm -rf chroma_db/*

test-query:
	curl -X POST http://localhost:8000/ask \
		-H "Content-Type: application/json" \
		-d '{"query": "What trading strategies are available?", "mode": "qa", "top_k": 5}' | jq

extract-spec:
	curl -X POST http://localhost:8000/ask \
		-H "Content-Type: application/json" \
		-d '{"query": "Extract a momentum trading strategy", "mode": "spec", "top_k": 10}' | jq

help:
	@echo "EminiPlayer RAG Service - Available commands:"
	@echo "  make build        - Build Docker image"
	@echo "  make up           - Start services"
	@echo "  make down         - Stop services"
	@echo "  make logs         - View logs"
	@echo "  make restart      - Restart services"
	@echo "  make ingest       - Ingest PDFs"
	@echo "  make stats        - Get database stats"
	@echo "  make health       - Health check"
	@echo "  make test-query   - Test QA query"
	@echo "  make extract-spec - Test spec extraction"
	@echo "  make clean        - Remove volumes and outputs"
