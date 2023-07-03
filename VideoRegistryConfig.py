#

import errno, os, winreg

class VideoRegistryConfig:
    """
    """
    class VideoAdapter:
        def __init__(self, K_Name):
            self.K_Name = K_Name
            self.K_VolatileSettings_GUID_Key = "{5b45201d-f2f2-4f3b-85bb-30ff1f953599}"
            self.K_VolatileSettings_GUID_Value = 0
            #
            self.DriverDate: str
            self.DriverDateData: str
            self.DriverDesc: str
            self.DriverVersion: str
            self.FutureScore: str
            self.InfPath: str
            self.InfSection: str
            self.MathcingDeviceId: str
            self.ProviderName: str

    def __init__(self, GUID: str):
        self.GUID = GUID
        self.K_Video_DeviceDesc: str
        self.K_Video_Driver: str
        self.K_Video_FeatureScore: str
        self.K_Video_Service: str

    def set_Video_Key_Data(self, DeviceDesc, Driver, FeatureScore, Service):
        self.K_Video_DeviceDesc = DeviceDesc
        self.K_Video_Driver = Driver
        self.K_Video_FeatureScore = FeatureScore
        self.K_Video_Service = Service

def populate_VideoRegistryConfig(key: winreg.HKEYType) ->VideoRegistryConfig:
    """
    """
    VRC_Obj = VideoRegistryConfig()
    return VRC_Obj
