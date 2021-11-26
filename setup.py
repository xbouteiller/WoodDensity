
# Import needed function from setuptools
from setuptools import setup

# Create proper setup to be used by pip
setup(name='WoodDensity',
      version='0.1',
      description='Compute wood density',
      author='Xavier Bouteiller',
      author_email='bouteiller.xavier@gmail.com',
      packages=['wooddensity'],
      install_requires=['pandas',
                        'configparser'])