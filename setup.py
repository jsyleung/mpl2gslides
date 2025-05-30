from setuptools import setup, find_packages

setup(
    name='mpl2gslides',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'google-api-python-client>=2.0.0',
        'google-auth-httplib2>=0.1.0',
        'google-auth-oauthlib>=0.4.0',
    ],
    author='Jason Leung',
    description='Draw Matplotlib plots as lines and shapes in Google Slides using the API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jsyleung/mpl2gslides',
    license='CC BY-NC 4.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Free for non-commercial use',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
