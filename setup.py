from distutils.core import setup

setup(name='ch-base',
      version='1.0',
      description='CogentHouse base station logger',
      author='James Brusey, Ross Wilkins',
      author_email='james.brusey@gmail.com',
      packages=['cogent.base', 'cogent.base.model', 'cogent.node'],
      data_files=[('/etc/init', ['etc/ch-sf.conf', 'etc/ch-base.conf']),
                  ('/etc/cron.daily', ['etc/yieldSender'])]
      )
