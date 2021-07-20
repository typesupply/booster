'''build RoboFont Extension'''

import os
from mojo.extensions import ExtensionBundle

# get current folder
basePath = os.path.dirname(__file__)

# source folder for all extension files
sourcePath = os.path.join(basePath, 'source')

# folder with python files
libPath = os.path.join(sourcePath, 'code')

# folder with html files
# htmlPath = os.path.join(sourcePath, 'documentation')

# folder with resources
# resourcesPath = os.path.join(sourcePath, 'resources')

# load license text from file
licensePath = os.path.join(basePath, 'LICENSE.txt')

# boolean indicating if only .pyc should be included
pycOnly = False

# name of the compiled extension file
extensionFile = 'Booster.roboFontExt'

# path of the compiled extension
buildPath = os.path.join(basePath, 'build')
extensionPath = os.path.join(buildPath, extensionFile)

# initiate the extension builder
B = ExtensionBundle()

# name of the extension
B.name = "Booster"

# name of the developer
B.developer = 'Type Supply'

# URL of the developer
B.developerURL = 'http://tools.typesupply.com'

# version of the extension
B.version = '0.2'

# should the extension be launched at start-up?
B.launchAtStartUp = True

# script to be executed when RF starts
B.mainScript = "main.py"

# script to be executed when the extension is unistalled
#B.uninstallScript = None

# does the extension contain html help files?
B.html = False

# minimum RoboFont version required for this extension
B.requiresVersionMajor = '3'
B.requiresVersionMinor = '1'

# scripts which should appear in Extensions menu
B.addToMenu = [
    {
        'path' : 'menu_showStatus.py',
        'preferredName': 'Booster Status',
        'shortKey' : '',
    } 
]

# license for the extension
with open(licensePath) as license:
    B.license = license.read()

# info for Mechanic extension manager
# B.repositoryURL = 'http://github.com/robodocs/rf-extension-boilerplate/'
# B.summary = 'A boilerplate extension which serves as starting point for creating your own extensions.'

# compile and save the extension bundle
print('building extension...', end=' ')
v = B.save(extensionPath, libPath=libPath, htmlPath=None, resourcesPath=None, pycOnly=pycOnly)
print('done!')
# check for problems in the compiled extension
print()
print(B.validationErrors())