# eroyee; experimental module for soapyMiri driver that should run Mirics-based hardware.
#
# Library / driver is from Erik here : https://github.com/ericek111/SoapyMiri, and
# Edouard here: https://github.com/f4exb/libmirisdr-4
#
# This is quite alpha, I've tested it with just one device which seems to work,
# but there seem to be some spurious signals, and in some cases it won't receive
# dead on the centre frequency. This could be simply a matter of settling on the best
# settings, or there could be something else more fundamental. Help welcome!
#
# There may be other settings to implement in time, just not yet.
#
# Best sampling rate for me is 8MHz, other rates I tried seemed to give errors after a 
# short time.
#
# If present you will need to blacklist the msi2500 device drivers. 
# See : https://www.radiosrs.net/msi2500_driver_conflicts.html

from owrx.source.soapy import SoapyConnectorSource, SoapyConnectorDeviceDescription
from owrx.form.input import Input, CheckboxInput, DropdownInput, DropdownEnum
from owrx.form.input.device import BiasTeeInput
from typing import List


class SoapymiriSource(SoapyConnectorSource):
    def getSoapySettingsMappings(self):
        mappings = super().getSoapySettingsMappings()
        mappings.update(
            {
                "bias_tee": "biasT_ctrl",
#                "device_type": "device_type", yet to be implemented?
                "if_mode": "if_mode",
            }
        )
        return mappings

    def getDriver(self):
        return "soapyMiri"


class IfModeOptions(DropdownEnum):
    IFMODE_ZERO_IF = "0"
    IFMODE_450 = "450000"
    IFMODE_1620 = "1620000"
    IFMODE_2048 = "2048000"

    def __str__(self):
        return self.value

# class DeviceTypeOptions(DropdownEnum):
#    DEVICE_TYPE_MIRI = "0"
#    DEVICE_TYPE_SDRPLAY = "1"
#
#    def __str__(self):
#        return self.value


class SoapymiriDeviceDescription(SoapyConnectorDeviceDescription):
    def getName(self):
        return "Miric-based device"

#    def getGainStages(self):  # Nope, these won't work!?
#        return ["RFGR", "IFGR"]

    def getInputs(self) -> List[Input]:
        return super().getInputs() + [
            BiasTeeInput(),
            DropdownInput(
                "if_mode",
                "IF Mode",
                IfModeOptions,
            ),
        ]

    def getDeviceOptionalKeys(self):
        return super().getDeviceOptionalKeys() + ["bias_tee", "if_mode"]

    def getProfileOptionalKeys(self):
        return super().getProfileOptionalKeys() + ["bias_tee", "if_mode"]

