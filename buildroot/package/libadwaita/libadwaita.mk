################################################################################
#
# libadwaita
#
################################################################################

LIBADWAITA_VERSION_MAJOR = 1.4
LIBADWAITA_VERSION = $(LIBADWAITA_VERSION_MAJOR).6
LIBADWAITA_SITE = https://download.gnome.org/sources/libadwaita/$(LIBADWAITA_VERSION_MAJOR)
LIBADWAITA_SOURCE = libadwaita-$(LIBADWAITA_VERSION).tar.xz
LIBADWAITA_INSTALL_STAGING = YES
LIBADWAITA_LICENSE = LGPL-2.1+
LIBADWAITA_LICENSE_FILES = COPYING
LIBADWAITA_DEPENDENCIES = libgtk4
LIBADWAITA_CONF_OPTS = -Dvapi=false -Dtests=false -Dexamples=false

ifeq ($(BR2_PACKAGE_GOBJECT_INTROSPECTION),y)
LIBADWAITA_CONF_OPTS += -Dintrospection=enabled
LIBADWAITA_DEPENDENCIES += gobject-introspection
else
LIBADWAITA_CONF_OPTS += -Dintrospection=disabled
endif

$(eval $(meson-package))
