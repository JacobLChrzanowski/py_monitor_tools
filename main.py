# Something for interpreting what displays you have connected and how large they are
#
#

import errno, os, winreg
import collections
import code
import math
import re
from code import interact
# proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
import VideoRegistryConfig as VRC
import Monitor as Monitor

import pyreadline3
import win32api
import pywintypes

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
    def __init__(self, hivename: str):
        """
        """
        self.hives = {"HKLM":winreg.HKEY_LOCAL_MACHINE}
        self.openHive = winreg.ConnectRegistry(None, self.hives[hivename])
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
# open_key_by_name(r"SYSTEM")


# monitors = win32api.EnumDisplayMonitors()
# monitor = Monitor.Monitor(monitors[0])
# print(monitor)

variables = globals().copy()
variables.update(locals())
shell = code.InteractiveConsole(variables)
# shell.interact()

# Registry testing
# regObj = Registry("HKLM")
# regObj.open_key_by_name(r"SYSTEM\CurrentControlSet\Control\Video")
# regObj.open_key_by_name(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
# regObj.open_key_by_name(r'SYSTEM\CurrentControlSet\Control\Video\{21B7EC77-5DC6-11EB-BA75-34CFF6E5C29C}')
# print(winreg.KEY_WOW64_32KEY)


import winreg
# print(r"*** Reading from %s ***" % aKey)
print("Start")
# test = winreg.OpenKey(aKey, "0000")
# test2 = winreg.EnumKey(aKey,0)
# print(test)
# print(test2)


class RegKey():
    """
    """
    def __init__(self, parentKey: winreg.HKEYType, selfKeyName: str = None, name = None) -> 'RegKey':
        """ pass selfKeyName to open that key under parentKey
        or pass None to have this key exist as the parentKey named as 'name'
        """
        if selfKeyName:
            # If we are opening a key under parentKey
            self.parentKey: winreg.HKEYType = parentKey
            self.name: str = selfKeyName
            self.openKey()
        else:
            # If we are instantiating this RegKey as the parent key
            self.key = parentKey
            self.name = name
            self.open = True

        self.valuesEnumerated = False
        self.valuesList = []
        self.valuesODict = collections.OrderedDict()

        self.openSubKeys = []

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
            self.openSubKeys.append(RegKey(self.key, keyName))
        return self.openSubKeys
    def closeEnumSubKeys(self):
        if self.openSubKeys:
            for openSubKey in self.openSubKeys:
                openSubKey.closeKey()
            self.openSubKeys.clear()
        else:
            print(f"No child keys to close: {self.name}")

    ### self Key Open/Close
    def openKey(self):
        try:
            self.key = winreg.OpenKey(self.parentKey, self.name)
            self.open = True
        except Exception as e:
            print(e)
            exit() #TODO: fix this

    def closeKey(self):
        if self.open:
            self.key.Close()
            self.open = False
        else:
            print(f"{self.name} already closed")

baseRegKeyHKLM = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
videoKey = winreg.OpenKey(baseRegKeyHKLM, r'SYSTEM\CurrentControlSet\Control\Video')
VideoConfigKeyNames = Registry.enumSubKeyNames(videoKey)
# print(f"enum VideoConfigKeyNames: {VideoConfigKeyNames}")
for VideoConfigKeyName in VideoConfigKeyNames:
    if VideoConfigKeyName != "{E0EC89FB-2A3A-11EB-BA6E-806E6F6E6963}":
        continue
    print(f"VideoConfigKeyName: {VideoConfigKeyName}")
    open_driverConfigKey = winreg.OpenKey(videoKey, VideoConfigKeyName)
    videoAdapters = Registry.enumSubKeyNames(open_driverConfigKey)
    # print(f"enum Drivers: {videoAdapters}")
    for videoAdapter in videoAdapters:
        print(f"Driver: {videoAdapter}")
        open_driverKey = winreg.OpenKey(open_driverConfigKey, videoAdapter)
        if videoAdapter == "Video":
            video_key_values = Registry.enumValues(open_driverKey)
            print(f"video_key_values items: {video_key_values.items()}")
        elif Registry.is_string_of_4_digits(videoAdapter):
            #TODO go deeper and enum values
            print('here')
        else:
            print("Found unexpected keyname under VideoConfigkey: {videoAdapter}")
        temp = Registry.enumSubKeyNames(open_driverKey)
        print(f"enum temp: {temp}")
        open_driverKey.Close()
    open_driverConfigKey.Close()
print("BEGIN TESTING")

videoKey = RegKey(videoKey, None, r"SYSTEM\CurrentControlSet\Control\Video")
VideoConfigKeyNames = videoKey.openEnumSubKeys()
for VideoConfigKey in VideoConfigKeyNames:
    if VideoConfigKey.name != "{21B7EC77-5DC6-11EB-BA75-34CFF6E5C29C}":
        continue
    print(f"VideoConfigKeyName: {VideoConfigKey.name}")
    videoAdapters = VideoConfigKey.openEnumSubKeys()
    for videoAdapter in videoAdapters:
        print(f"Driver: {videoAdapter.name}")
        if videoAdapter.name == "Video":
            video_key_values = videoAdapter.getValuesList()
            print(f"video_key_values items: {video_key_values}")
        elif Registry.is_string_of_4_digits(videoAdapter.name):
            #TODO go deeper and enum values
            key_values = videoAdapter.getValuesList()
            for value in key_values:
                print(value)
        else:
            print("Found unexpected keyname under VideoConfigkey: {videoAdapter}")

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