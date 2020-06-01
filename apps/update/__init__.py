
import os


sysUserPath = os.path.expanduser('~')

packagePath = sysUserPath + "/package"

if os.path.exists(packagePath):
    pass
else:
    os.mkdir(packagePath)


testpackagePath = packagePath + "/test"
if os.path.exists(testpackagePath):
    pass
else:
    os.mkdir(testpackagePath)


officialpackagePath = packagePath + "/official"
if os.path.exists(officialpackagePath):
    pass
else:
    os.mkdir(officialpackagePath)


#print(testpackagePath,officialpackagePath)