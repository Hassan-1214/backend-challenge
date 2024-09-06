# Define the virtual environment directory
VENV_DIR = env

# Define the Django server command
DJANGO_SERVER_CMD = python manage.py runserver 0.0.0.0:8080

# Define the path to the requirements file
REQUIREMENTS_FILE = requirements.txt

# Create the virtual environment and install requirements
env:
	@python3 -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

# Make migrations
migrations: env
	@$(VENV_DIR)/bin/python manage.py makemigrations

# Apply migrations
migrate: migrations
	@$(VENV_DIR)/bin/python manage.py migrate

# Run pytest
test: env
	@$(VENV_DIR)/bin/pytest task/

# Run flake8
flake8: env
	@$(VENV_DIR)/bin/flake8

# Open Django shell
shell: env
	@$(VENV_DIR)/bin/python manage.py shell

# Run Django server
runserver: env
	@$(DJANGO_SERVER_CMD)

# Install requirements
install-requirements: env
	@$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

# All tasks combined
all: env migrate test flake8 runserver
	@echo "All tasks completed."

# Default target
.PHONY: venv migrations migrate test flake8 shell runserver install-requirements all
