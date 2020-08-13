.PHONY: build

export HARVEST_LOGLEVEL=DEBUG
export XHARVEST_LOGLEVEL=DEBUG

flatpak_dir=flatpak
mode=pypi
company=velvetkeyboard
project=xharvest

# [Virtualenv Bins]
# -----------------------------------------------------------------------------
venv=env
python=$(venv)/bin/python
linter=$(venv)/bin/flake8

# [Semver]
# -----------------------------------------------------------------------------
git_version=$(shell git describe --tags)
xharvest_version=$(shell $(python) -m xharvest.__init__)
docker_tag=$(xharvest_version)

check_semver:
ifneq ($(git_version),$(xharvest_version))
	@echo "$(git_version) != $(xharvest_version)"
	@exit 1
endif

ifeq ($(mode),docker)
	builder_shell=docker run --rm -ti -w /app -v $$PWD/:/app:Z xharvest:builder bash -c 
endif

ifeq ($(mode),bash)
	builder_shell=bash -c 
endif

run:
ifeq ($(mode),pypi)
	./env/bin/pip install .
	./env/bin/xharvest
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

lint:
	$(linter) xharvest/

todo:
	grep -rnw xharvest -e "# TODO"

fixme:
	grep -rnw xharvest -e "# FIXME"

update_assets:
	-rm data/hicolor/16x16/xharvest.png
	-rm data/hicolor/32x32/xharvest.png
	-rm data/hicolor/48x48/xharvest.png
	-rm data/hicolor/128x128/xharvest.png
	-rm xharvest/data/img/xharvest.png
	cp -f assets/logo-16.png data/hicolor/16x16/xharvest.png
	cp -f assets/logo-32.png data/hicolor/32x32/xharvest.png
	cp -f assets/logo-48.png data/hicolor/48x48/xharvest.png
	cp -f assets/logo-128.png data/hicolor/128x128/xharvest.png
	cp -f assets/logo-128.png xharvest/data/img/xharvest.png

# [Building]
# -----------------------------------------------------------------------------

build_pypi: lint
	$(python) setup.py sdist --formats=zip,gztar,xztar
	$(python) setup.py bdist_wheel

build_rpm: lint
	$(python) setup.py bdist_rpm

build_flatpak: lint
	mkdir -p flatpak/pypi/
	pip wheel . -e .[flatpak] -w flatpak/pypi/
	mkdir -p flatpak/build
	cd $(flatpak_dir) && \
		flatpak-builder build-dir \
			--force-clean \
			org.velvetkeyboard.xHarvest.yml

build_docker: lint
	docker build . -t $(company)/$(project):$(docker_tag)

build_all: build_pypi build_rpm build_flatpak build_docker

# [Publish]
# -----------------------------------------------------------------------------

pypi=test

ifeq ($(pypi),test)
	pypi_url=https://test.pypi.org/legacy/
endif
ifeq ($(pypi),production)
	pypi_url=https://upload.pypi.org/legacy/
endif


publish_pypi: check_semver build_pypi
	twine upload \
		--repository-url $(pypi_url) \
		dist/xharvest-$(xharvest_version)-py3-none-any.whl

