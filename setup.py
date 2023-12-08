from setuptools import setup, find_packages

setup(
    name='pyqtplotlib',
    version='1.0.0',
    author='SR',
    description="A Python library designed to simplify the development of scientific GUI applications, providing a plotting syntax similar to Matplotlib's pyplot.",
    packages=find_packages(),  # Automatically discover and include all packages
    install_requires=[
        # List the dependencies your package needs
        'pyqt5',
        'pyqtgraph>=0.12.4',
        'numpy',
        'scipy',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            # Define any command-line scripts your package provides
            # 'your_script_name=your_package.module:function_name',
        ],
    },
)
