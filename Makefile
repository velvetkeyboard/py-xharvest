.PHONY: build

flatpak_dir=flatpak
mode=pypi
docker_tag=local


# export HARVEST_LOGLEVEL=DEBUG
export XHARVEST_LOGLEVEL=DEBUG

run:
ifeq ($(mode),pypi)
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
ifeq ($(mode),docker)
	docker run \
		-e DISPLAY=$DISPLAY \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		velvetkeyboard/xharvest:$(docker_tag)
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


update_assets:
	-rm data/hicolor/16x16/xharvest.png
	-rm data/hicolor/32x32/xharvest.png
	-rm data/hicolor/48x48/xharvest.png
	-rm xharvest/data/img/xharvest.png
	cp -f assets/logo-16.png data/hicolor/16x16/xharvest.png
	cp -f assets/logo-32.png data/hicolor/32x32/xharvest.png
	cp -f assets/logo-48.png data/hicolor/48x48/xharvest.png
	cp -f assets/logo-128.png xharvest/data/img/xharvest.png