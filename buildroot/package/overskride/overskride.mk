################################################################################
#
# overskride
#
################################################################################

# 0.4.5
OVERSKRIDE_VERSION = v0.5.7
OVERSKRIDE_SITE = $(call github,kaii-lb,overskride,$(OVERSKRIDE_VERSION))
OVERSKRIDE_LICENSE = GPL-3.0
OVERSKRIDE_LICENSE_FILES = COPYING
OVERSKRIDE_INSTLL_STAGING = YES
OVERSKRIDE_DEPENDENCIES = dbus libadwaita librsvg pulseaudio

$(eval $(cargo-package))