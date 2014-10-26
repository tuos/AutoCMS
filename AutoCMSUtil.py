import re 

def LoadConfiguration(configFileName):

  config = dict()

  with open(configFileName,'r') as configFile:
    configIn = configFile.read().splitlines()

  for line in configIn:
    if( re.match(r'export',line) ):
      varKey = line.split('=')[0]
      varKey = varKey.replace("export","")
      varKey = varKey.strip()
      varValue = varValue = line.split('=')[1]
      varValue = varValue.strip()
      config[varKey] = varValue

  return config
