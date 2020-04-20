.PHONY: build

flatpak_dir=flatpak
mode=pypi
docker_tag=local


run:
ifeq ($(mode),)
	./env/bin/pip install . && ./env/bin/xharvest
endif
ifeq ($(mode),flatpak)
	cd $(flatpak_dir) && \
		flatpak-builder \
			--run \
			--verbose \
			build-dir \
			org.velvetkeyboard.xHarvest.yml xharvest
endif


build:
ifeq ($(mode),pypi)
	python setup.py sdist bdist_wheel
endif
ifeq ($(mode),flatpak)
	mkdir -p flatpak/pypi/
	pip wheel . -e .[flatpak] -w flatpak/pypi/
	mkdir -p flatpak/build
	cd $(flatpak_dir) && \
		flatpak-builder build-dir \
			--force-clean \
			org.velvetkeyboard.xHarvest.yml
endif
ifeq ($(mode),rpm)
	mkdir -p build/$(mode)/
endif
ifeq ($(mode),docker)
	docker build . -t velvetkeyboard/xharvest:$(docker_tag)
endif
