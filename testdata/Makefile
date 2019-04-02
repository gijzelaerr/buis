.PHONY: docker docker-shell

DOCKER_ID=random_fits

docker:
	docker build . -t ${DOCKER_ID}

docker-shell:
	docker run -ti ${DOCKER_ID} bash