# sudo dnf remove -y \
# 	toolbox \
# 	conmon \
# 	containernetworking-plugins \
# 	containers-common \
# 	crun \
# 	flatpak-session-helper \
# 	fuse3 \
# 	fuse3-libs \
# 	podman \
# 	podman-plugins \
# 	fuse-overlayfs \
# 	libvarlink-util \
# 	slirp4netns
sudo dnf remove -y \
	gcc \
	binutils \
	binutils-gold \
	cpp \
	isl \
	libmpc

sudo dnf remove -y python3-devel

sudo dnf remove -y cairo-devel \
	bzip2-devel \
	expat-devel \
	fontconfig-devel \
	freetype-devel \
	glib2-devel \
	libX11-devel \
	libXau-devel \
	libXext-devel \
	libXrender-devel \
	libblkid-devel \
	libffi-devel \
	libmount-devel \
	libpng-devel \
	libselinux-devel \
	libsepol-devel \
	libxcb-devel \
	pcre-cpp \
	pcre-devel \
	pcre-utf16 \
	pcre-utf32 \
	pcre2-devel \
	pcre2-utf16 \
	pixman-devel \
	xorg-x11-proto-devel \
	zlib-devel

sudo remove -y gobject-introspection-devel \
	autoconf \
	automake \
	libtomcrypt \
	libtommath \
	libtool \
	m4 \
	perl-Thread-Queue \
	python3-asn1crypto \
	python3-cffi \
	python3-cryptography \
	python3-mako \
	python3-markupsafe \
	python3-paste \
	python3-ply \
	python3-pyOpenSSL \
	python3-pycparser \
	python3-tempita \
	python3-beaker \
	python3-crypto

sudo dnf remove -y cairo-gobject-devel