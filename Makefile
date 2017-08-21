

build:
	@docker build -t inasafe/inasafe-realtime .

up:
	@docker-compose up -d inasafe-realtime

logs:
	@docker-compose logs inasafe-realtime

down:
	@docker-compose down
