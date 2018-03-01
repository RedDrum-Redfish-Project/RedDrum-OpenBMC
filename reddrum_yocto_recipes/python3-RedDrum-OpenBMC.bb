SUMMARY = "A python based Redfish service for the OpenBMC using the RedDrum Redfish Service"

DESCRIPTION = "A redfish OpenBMC backend  implementation"
HOMEPAGE = "https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC"
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=ab0435b88061e67b94d71da4a3297591"

SRC_URI = "git://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC"
SRCREV = "${AUTOREV}"
S="${WORKDIR}/git"

FILES_${PN} += "${datadir}/RedDrum"

inherit setuptools3

RDEPENDS_$PN = "${PYTHON_PN}-RedDrum-Frontend"
