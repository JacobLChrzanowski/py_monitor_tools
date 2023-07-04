# Something for interpreting what displays you have connected and how large they are
#
#

import os, sys, errno, winreg, traceback
import collections
import code
import math
import re
import logging
from code import interact
# proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
import VideoRegistryConfig as VRC
import Monitor as Monitor

import pyreadline3
import win32api
import pywintypes

logging.basicConfig(level = logging.DEBUG)
LOG = logging.getLogger(__name__)

def closeKeys(keys: list[winreg.HKEYType]):
    if type(keys) == winreg.HKEYType:
        keys.Close()
        return
    for key in keys:
        key.Close()
        return

class Registry():
    """
    """
    enumValues_LoopLimit = 1000
    string_of_4_digits = re.compile(r"^\d{4}$")
    arch_keys = (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY)
    hives = {"HKLM":winreg.HKEY_LOCAL_MACHINE}

    def __init__(self, hivename: str):
        """
        """
        self.openHive = winreg.ConnectRegistry(None, Registry.hives[hivename])
        self.lastKey = None
        self.currentKey = None

    def open_key_by_name(self, key_name: str):
        self.lastKey = self.currentKey
        self.currentKey = winreg.OpenKey(self.openHive, key_name)
        print(self.currentKey)

    def is_string_of_4_digits(inputString: str) -> bool:
        re_match = re.match(Registry.string_of_4_digits, inputString)
        if re_match:
            return True
        else:
            return False

    def enumValues(openKey: winreg.HKEYType, out_oDict: collections.OrderedDict = None) -> collections.OrderedDict:
        """
        enumValues takes an open registry key and returns an Ordered Dict of the values on that key
        If out_oDict is pre-supplied it will be modified in place to include values on that key
        """
        if out_oDict == None:
            out_oDict = collections.OrderedDict()
        count = 0
        while True:
            if count > Registry.enumValues_LoopLimit:
                break
            try:
                enum_tuple = winreg.EnumValue(openKey, count)
                out_oDict[enum_tuple[0]] = (enum_tuple[1], enum_tuple[2])
            except OSError as e:
                break
            count += 1
        return out_oDict
    
    def enumSubKeyNames(givenKey: winreg.HKEYType) -> list[str]:
        """
        """
        keySubkeys, keyValues, keyModtime = winreg.QueryInfoKey(givenKey)
        # print(f"enumSubKeyNames. keySubKeys: {keySubkeys}")
        outKeyNames = []
        for i in range(keySubkeys):
            try:
                aValue_name = winreg.EnumKey(givenKey, i)
                # oKey = winreg.OpenKey(aKey, aValue_name)
                outKeyNames.append(aValue_name)
                # sValue = winreg.QueryValueEx(oKey, "DisplayName")
                # print(sValue)
            except EnvironmentError as e:
                print(e)
                break
        return outKeyNames
    # interact()


variables = globals().copy()
variables.update(locals())
shell = code.InteractiveConsole(variables)
# shell.interact()


class RegKey():
    """
    """
    hives = {"HKLM":(winreg.HKEY_LOCAL_MACHINE, 'HKEY_LOCAL_MACHINE')}

    def __init__(self, parentRegKey: 'RegKey', selfKeyName: str = None, bootstrapKey: winreg.HKEYType = None) -> 'RegKey':
        """ pass selfKeyName to open that key under parentKey
        or pass None to have this key exist as the parentKey named as 'name'
        """
        if parentRegKey is None and bootstrapKey is not None:
            # We are not being passed a RegKey instance
            # We are in the process of bootstrpaping this object
            self.key = bootstrapKey
            self.name = selfKeyName
            self.path = 'Computer\\' + self.name + '\\'
        elif parentRegKey is not None and bootstrapKey is not None:
            LOG.error('You cannot pass a parentRegKey and a boostrapKey to RegKey at the same time!')
            raise Exception
        else:
            # If we are opening a key under parentRegKey
            # self.name :: This could do better as selfKeyName.split('\\')[-1] but then you would have to contend with refactoring openKey
            self.parentKey: 'RegKey' = parentRegKey
            self.name:      str = selfKeyName
            self.path:      str = parentRegKey.path + '\\' + selfKeyName
            self.openKey()
        # else:
        #     # If we are instantiating this RegKey as the already open parent key
        #     self.key:           winreg.HKEYType = parentRegKey
        #     self.name:          str = name
        #     self.open:          bool = True

        self.valuesEnumerated:  bool = False
        self.valuesList:        list['str'] = []
        self.valuesODict:       collections.OrderedDict = collections.OrderedDict()

        self.openSubKeys:       list['RegKey'] = []

    def ConnectHive(hivename: str):
        """
        """
        new_OpenHive = winreg.ConnectRegistry(None, RegKey.hives[hivename][0])
        new_OpenHiveName = RegKey.hives[hivename][1]
        new_RegKey = RegKey(None, selfKeyName = new_OpenHiveName, bootstrapKey=new_OpenHive)
        return new_RegKey
    
    def __str__(self):
        outStr = ""
        outStr += f'{self.name} :: {self.path}'
        return outStr
    
    def __repr__(self):
        outStr = ""
        outStr += f'{self.name} :: {self.path}'
        return outStr

    ### value Operations
    def enumValues(self):
        Registry.enumValues(self.key, self.valuesODict)
        self.valuesList = list(self.valuesODict.items())
        self.valuesEnumerated = True
    def getValuesList(self, clobber=False) -> list['str']:
        if clobber == True or self.valuesEnumerated == False:
            self.enumValues()
        return self.valuesList
    def getValuesODict(self, clobber=False) -> collections.OrderedDict:
        if clobber == True or self.valuesEnumerated == False:
            self.enumValues()
        return self.valuesList

    
    ### subkKey Operations
    def enumSubKeyNames(self) -> list['str']:
        self.subKeyNames = Registry.enumSubKeyNames(self.key)
        return self.subKeyNames
    def openEnumSubKeys(self) -> list['RegKey']:
        if len(self.openSubKeys) != 0:
            for key in self.openSubKeys:
                key.Close()
        self.openSubKeys.clear()
        self.enumSubKeyNames()
        for keyName in self.subKeyNames:
            self.openSubKeys.append(RegKey(self, keyName))
        return self.openSubKeys
    def closeSubKeys(self, closeSelf = False, deleteSubKeys = False):
        for key in reversed(self.openSubKeys):
            # We must iterate in reverse so we don't end up deleting just every other
            # element due to i not matching list iteration correctly
            key.closeSubKeys(closeSelf=True, deleteSubKeys=deleteSubKeys)
            if deleteSubKeys:
                # self.openSubKeys.remove(key)
                del self.openSubKeys[self.openSubKeys.index(key)]
        if closeSelf:
            self.closeKey()
    def openSubKey(self, subKeyName: str) -> 'RegKey':
        newOpenSubKey = RegKey(self, subKeyName)
        self.openSubKeys.append(newOpenSubKey)
        return newOpenSubKey

    ### self Key Open/Close
    def openKey(self):
        try:
            self.key = winreg.OpenKey(self.parentKey.key, self.name)
            self.open = True
        except Exception as e:
            LOG.error(e)
            LOG.error(f"self.name = {self.name}")
            # traceback.print_exception(*sys.exc_info())
            raise e
            exit() #TODO: fix this

    def closeKey(self):
        if self.open:
            self.key.Close()
            self.open = False
        else:
            LOG.warn(f"{self.name} already closed")


print("Start")
open_HKLM = RegKey.ConnectHive('HKLM')
print(open_HKLM)
videoKey = open_HKLM.openSubKey(r'SYSTEM\CurrentControlSet\Control\Video')
print(videoKey)
a = videoKey.openEnumSubKeys()
for i in a:
    print(i)
exit()
baseRegKeyHKLM_raw = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# videoKey = winreg.OpenKey(KeyHKLM, r'SYSTEM\CurrentControlSet\Control\Video')
baseRegKeyHKLM = RegKey(baseRegKeyHKLM_raw, None, r"HKLM\\")
videoKey = baseRegKeyHKLM.openSubKey(r'SYSTEM\CurrentControlSet\Control\Video')
print(baseRegKeyHKLM.name)
print(videoKey.name)
print('')
print(winreg.QueryInfoKey(baseRegKeyHKLM.key))
key_path = winreg.QueryPathEx(baseRegKeyHKLM.key, 6)
winreg.Query
exit()

# graphicsDriverConfiguration = RegKey(videoKey, None, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Configuration")
# graphicsDriverConfiguration = videoKey.openSubKey(r"Configuration")
graphicsDriverConfiguration = videoKey.openEnumSubKeys()
print(graphicsDriverConfiguration)
print("\n\nEND")
exit()
gDCKeys = graphicsDriverConfiguration.openEnumSubKeys()
for subKey in gDCKeys:
    latestSubKey = ''
    latestTime = 0
    currentSubKeyValuesDict = subKey.getValuesODict()
    if 'Timestamp' not in currentSubKeyValuesDict:
        LOG.error(f"{subKey.name} did not have a 'Timestamp' value")
        continue
    print(type(currentSubKeyValuesDict['Timestamp']))
    print(currentSubKeyValuesDict['Timestamp'])

# VideoConfigKeyNames = videoKey.openEnumSubKeys()
# for VideoConfigKey in VideoConfigKeyNames:
#     if VideoConfigKey.name != "{21B7EC77-5DC6-11EB-BA75-34CFF6E5C29C}":
#         continue
#     # print(f"VideoConfigKeyName: {VideoConfigKey.name}")
#     videoAdapters = VideoConfigKey.openEnumSubKeys()
#     for videoAdapter in videoAdapters:
#         # print(f"Driver: {videoAdapter.name}")
#         if videoAdapter.name == "Video":
#             video_key_values = videoAdapter.getValuesList()
#             # print(f"video_key_values items: {video_key_values}")
#         elif Registry.is_string_of_4_digits(videoAdapter.name):
#             #TODO go deeper and enum values
#             key_values = videoAdapter.getValuesList()
#             for value in key_values:
#                 # print(value)
#                 pass
#         else:
#             pass
#             # print("Found unexpected keyname under VideoConfigkey: {videoAdapter}")

LOG.info('Closing keys')
graphicsDriverConfiguration.closeSubKeys(deleteSubKeys=True)
print(graphicsDriverConfiguration.openSubKeys)

videoKey.closeKey()
# closeKeys(videoKey)








########
# print(videoKeyNames)



#####
# REG_PATH = r"Control Panel\Mouse"
# registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
#                                        winreg.KEY_READ)
# print(registry_key)

# win32api.GetMonitorInfo()


# print('here')
# import subprocess
# import winreg

# print(subprocess.check_output('whoami.exe /groups /fo list', text=True))

# hkey = winreg.HKEY_LOCAL_MACHINE
# winreg.OpenKey(hkey, 'SOFTWARE', 0, winreg.KEY_READ)