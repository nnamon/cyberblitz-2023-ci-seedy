tag = cyberblitz-2023-ci-seedy
port = 31337

build:
	docker build -t $(tag) --file Dockerfile .

run:
	docker run -it --rm -p $(port):31337 $(tag)

dev:
	docker run -it --rm -p $(port):31337 -v `pwd`:/opt/ciseedy/ $(tag) /bin/bash

daemon:
	docker run -dt -p $(port):31337 $(tag)

