.PHONY: build

build_dir=build/flatpak/
mode=pypi

run:
	./env/bin/pip install . && ./env/bin/xharvest
ifeq ($(mode),flatpak)
	flatpak-builder --run $(build_dir) org.velvetkeyboard.xHarvest.yml xharvest
endif


build:
ifeq ($(mode),pypi)
	python setup.py sdist bdist_wheel
endif
ifeq ($(mode),flatpak)
	mkdir -p build/flatpak/
	flatpak-builder build --share=network $(build_dir) org.velvetkeyboard.xHarvest.yml xharvest
endif
ifeq ($(mode),rpm)
	mkdir -p build/$(mode)/
endif
