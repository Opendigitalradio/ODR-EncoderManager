from distutils.core import setup, Extension

lameenc = Extension(
    'lameenc',
    include_dirs=["/usr/include", "/usr/include/lame"],
    libraries=['mp3lame'],
    library_dirs=["/usr/lib"],
    sources=['lameenc.c']
)

setup(name = 'lameenc',
       version = '1.2.1',
       description = 'lameenc from https://github.com/chrisstaite/lameenc',
       ext_modules = [lameenc])
