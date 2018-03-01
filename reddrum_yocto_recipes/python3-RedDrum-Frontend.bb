SUMMARY = "The common Frontend App for RedDrum Redfish Servers"

DESCRIPTION = "A redfish frontend server implementation"
HOMEPAGE = "https://github.com/RedDrum-Redfish-Project/RedDrum-Frontend"
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=ab0435b88061e67b94d71da4a3297591"

SRC_URI = "git://github.com/RedDrum-Redfish-Project/RedDrum-Frontend"
SRCREV = "${AUTOREV}"
S="${WORKDIR}/git"

FILES_${PN} += "${datadir}/RedDrum"

inherit setuptools3

RDEPENDS_${PN} = "${PYTHON_PN}-flask ${PYTHON_PN}-json ${PYTHON_PN}-netclient ${PYTHON_PN}-misc ${PYTHON_PN}-setuptools ${PYTHON_PN}-dbus ${PYTHON_PN}-passlib ${PYTHON_PN}-pytz glibc-utils localedef apache2"
