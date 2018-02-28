from setuptools import setup

setup(name='RedDrum-OpenBMC',
      version='0.9.5',
      description='A python Redfish Service for the OpenBMC',
      author='RedDrum-Redfish-Project / Paul Vancil, Dell ESI',
      author_email='redDrumRedfishProject@gmail.com',
      license='BSD License',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Libraries :: Embedded Systems',
          'Topic :: Communications'
      ],
      keywords='Redfish RedDrum SPMF OpenBMC ',
      url='https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC',
      download_url='https://github.com/RedDrum-Redfish-Project/RedDrum-OpenBMC/archive/0.9.5.tar.gz',
      packages=['reddrum_openbmc'],
      scripts=['scripts/redDrumObmcMain'],
      package_data={'reddrum_openbmc': ['getObmcIpInfo.sh','getObmcProtocolInfo.sh'] },
      install_requires=[
          'RedDrum-Frontend==0.9.5', # the common RedDrum Frontend code that has dependency on Flask
          'passlib==1.7.1',          # used by Frontend
          'Flask',                   # used by Frontend
          'pytz'                     # used by Frontend
          # obmc.mapper
          # dbus
      ],
)
