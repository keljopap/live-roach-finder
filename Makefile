
run-frontend:
	@echo "Running frontend..."
	@cd frontend/map-frontend && npm start

init:
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt

run-server:
	open http://localhost:50000/businesses & # to view the api output
	python main.py #to spin up the api server