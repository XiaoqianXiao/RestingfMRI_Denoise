import setuptools
from os.path import join, dirname
import glob

__dir_path = dirname(__file__)

if __name__ == '__main__':
    with open(join(__dir_path, "requirements.txt"), 'r') as fh:
        requirements = [line.strip() for line in fh]
    with open(join(__dir_path, "README.md")) as fh:
        long_description = "".join(fh.readlines())
    setuptools.setup(
        name = "RestingfMRI_Denoise",
        version = "0.0.1",
        author = "XiaoXiaoqian",
        author_email = "xiaoqian@stanford.edu",
        description = "RestingfMRI_Denoise - preprocessing of resting fMRI data automatically and base on customized demands",   
        long_description=long_description,
        long_description_content_type="text/x-rst",
        license="MIT",
        url="https://github.com/XiaoXiaoqian/RestingfMRI_Denoise",
        classifiers=[
            'Development Status :: 1 - Beta',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            "Programming Language :: Python :: 3.7",
        ],
        packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*tests*",
                                                   '*build_tests*']),
        include_package_data=True,
        install_requires=requirements,
        scripts=[join('RestingfMRI_Denoise', 'scripts', 'RestingfMRI_Denoise')]
    )
