from setuptools import setup

setup(name='mooc',
      version='1.0',
      description='8bitmooc',
      author='Barry Peddycord III',
      author_email='admin@8bitmooc.org',
      url='http://8bitmooc.org',
      install_requires=['Django>=1.5',
                        'django-bootstrap-toolkit',
                        'django-avatar',
                        'South>=0.7',
                        'py-bcrypt',
                        'pytz',
                        'django-redis',
                        'markdown',
                        'Pygments',
                        'pypng',
                        'pil'],
     )
