from setuptools import setup
from glob import glob
import os

package_name = 'rover_global_localization'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Samuel Gendre',
    maintainer_email='samuel16.gendre@gmail.com',
    description='Global GPS localization for a rover using robot_localization.',
    license='MIT',
    entry_points={
        'console_scripts': [
        ],
    },
)