from setuptools import setup, find_packages

setup(
    name='telegram-login-ui',
    version='1.0.9',
    description='A package to create a simple UI for logging into Telegram accounts and managing sessions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Saeid Moini',
    author_email='saeid.moini1997@gmail.com',
    url='https://github.com/saeidmoini/telegram-login-ui',
    packages=find_packages(),  # Ensure this is included
    install_requires=[
        'Flask>=2.0.0',
        'python-dotenv>=0.21.0',
        'telethon>=1.24.0',
        'pyjwt>=2.6.0',
    ],
    package_data={
        '': ['templates/*'],  # Include templates in the package
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)