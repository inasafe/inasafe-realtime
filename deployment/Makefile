SHELL := /bin/bash

PROJECT_ID := realtime

default: build deploy status

build:
	@echo
	@echo "--------------------------"
	@echo "Building"
	@echo "--------------------------"
	@docker-compose -p $(PROJECT_ID) build

ansible-check:
	@echo "Check ansible command"
	@ansible -i ansible/development/hosts all -m ping
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml --check --list-tasks --list-hosts $(ANSIBLE_ARGS)

setup-ansible:
	@echo "Setup configurations using ansible"
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml -v $(ANSIBLE_ARGS)

up:
	@echo
	@echo "--------------------------"
	@echo "Bringing up fresh instances"
	@echo "--------------------------"
	@docker-compose -p $(PROJECT_ID) up -d

down:
	@docker-compose -p $(PROJECT_ID) down

status:
	@echo
	@echo "--------------------------"
	@echo "Show status of all containers"
	@echo "--------------------------"
	@docker-compose -p $(PROJECT_ID) ps
