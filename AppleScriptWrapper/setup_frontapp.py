from distutils.core import setup, Extension

module1 = Extension('front_app',
                    sources = ['front_app.m'],
                    extra_link_args=[
                        '-framework', 'Python',
                        '-framework', 'Foundation',
                        '-framework', 'AppKit'
                        ]
                    )

setup (name = 'AppleScriptTools',
       version = '1.0',
       description = 'This is my first',
       ext_modules = [module1])
