from setuptools import setup

setup(name="vpp",
      version="zero",
      description="",
      url="https://github.com/Aeva/switchprint",
      author="Aeva Palecek",
      author_email="aeva.ntsc@gmail.com",
      license="GPLv3",
      packages=["vpp"],
      zip_safe=False,

      entry_points = {
        "console_scripts" : [
            "vpp=vpp.vpp:gui_main",
            ],
        },

      install_requires = [
        ])
      
