#

import math
import pywintypes, win32api

class Monitor():
    # PyHANDLE_Type -> <class 'PyHANDLE'>
    PyHANDLE_Type = type(pywintypes.HANDLE())
    def __init__(self, monitor_tuple: tuple):
        """
        monitor_tuple ->
        (<PyHANDLE:65539>, <PyHANDLE:0>, (2560, 0, 5120, 1440))

        win32api.GetMonitorInfo(self.monitor_handle) ->
        {'Monitor': (2560, 0, 5120, 1440), 'Work': (2560, 0, 5120, 1400), 'Flags': 0, 'Device': '\\\\.\\DISPLAY2'}
        """
        assert len(monitor_tuple) == 3
        assert type(monitor_tuple[0]) == self.PyHANDLE_Type
        assert type(monitor_tuple[0]) == self.PyHANDLE_Type
        assert type(monitor_tuple[2]) == tuple
        assert len(monitor_tuple[2]) == 4

        self.monitor_handle = int(monitor_tuple[0])
        self.screen_space_monitor_rect = monitor_tuple[2]
        self.dim_width, self.dim_height = self.get_dimensions_from_rect(self.screen_space_monitor_rect)
        self.ratio_w, self.ratio_h, self.ratio_divisor = self.get_ratio_from_dimensions(self.dim_width, self.dim_height)
        temp_monitorInfo = win32api.GetMonitorInfo(self.monitor_handle)
        self.screen_space_work_rect = temp_monitorInfo['Work']
        self.flags = temp_monitorInfo['Flags']
        self.deviceIdentifier = temp_monitorInfo['Device']
        self.dim_work_width, self.dim_work_height = self.get_dimensions_from_rect(self.screen_space_work_rect)

    def transform_to_screen_space(self, x: int, y: int):
        screen_space_x = self.screen_space_monitor_rect[0] + x
        screen_space_y = self.screen_space_monitor_rect[2] + y
        return screen_space_x, screen_space_y
    def transform_to_local_space(self, x: int, y: int):
        screen_space_x = x - self.screen_space_monitor_rect[0]
        screen_space_y = y - self.screen_space_monitor_rect[2]
        return screen_space_x, screen_space_y

    def get_dimensions_from_rect(self, screen_space_rect: tuple):
        """
        screen_space_rect -> (2560, 0, 5120, 1440)
        2560 -> upper left x, 0 -> upper left y
        5120 -> lower right x, 1440 -> lower right y
        """
        width = screen_space_rect[2]-screen_space_rect[0]
        height = screen_space_rect[3]-screen_space_rect[1]
        return width, height

    def get_ratio_from_dimensions(self, width: int, height: int):
        gcd = math.gcd(width, height)
        return int(width/gcd), int(height/gcd), int(gcd)

    def __str__(self):
        return "" +\
            f"Monitor: {self.deviceIdentifier:<14} HandleId: {self.monitor_handle:<7}\n" +\
            f"Width: {self.dim_width:<5} Height: {self.dim_height:<5}\n" +\
            f"Ratio: {self.ratio_w}:{self.ratio_h}\n" +\
            f"Flags: {self.flags}\n" +\
            f"Work Width: {self.dim_work_width:<5} Height: {self.dim_work_height:<5}"
