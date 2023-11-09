from setuptools import setup, find_packages

setup(
    name='gui',
    version='1.0.0',
    author='SR',
    author_email='your.email@example.com',
    description='A general purpose GUI for plotting and data analysis in python',
    packages=find_packages(),  # Automatically discover and include all packages
    install_requires=[
        # List the dependencies your package needs
        'pyqt5',
        'pyqtgraph',
        'numpy',
        'scipy',
        'matplotlib',
    ],
    classifiers=[
        # 'Development Status :: 3 - Alpha',
        # 'Intended Audience :: Developers',
        # 'License :: OSI Approved :: MIT License',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        # Add other classifiers as needed
    ],
    entry_points={
        'console_scripts': [
            # Define any command-line scripts your package provides
            # 'your_script_name=your_package.module:function_name',
        ],
    },
)
