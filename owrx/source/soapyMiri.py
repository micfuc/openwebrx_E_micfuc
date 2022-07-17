# eroyee; experimental module for soapyMiri driver that should run Mirics-based hardware.
#
# Library / driver is from Erik here : https://github.com/ericek111/SoapyMiri, and
# Edouard here: https://github.com/f4exb/libmirisdr-4
#
# This is quite alpha, I've tested it with just one device which seems to work,
# but there may be some spurious signals, and in some cases it won't receive
# dead on the centre frequency. This should be addressable by setting an offset.
# 
# Help to improve this is welcome, and there may be other settings to implement
# in time, just not yet.
#
# Sampling rate should be set at specified values such as 2, 5, 8 MHz, other rates 
# can give errors.
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
                "offset_tune": "offset_tune_ctrl",
                "bufflen": "bufflen",
            }
        )
        return mappings

    def getDriver(self):
        return "soapyMiri"

class BuffLenOptions(DropdownEnum):
    BUFFLEN_15872 = "15872"
    BUFFLEN_36864 = "36864"
    BUFFLEN_73728 = "73728"

    def __str__(self):
        return self.value

class SoapymiriDeviceDescription(SoapyConnectorDeviceDescription):
    def getName(self):
        return "Miric-based device (via SoapySDR)"

#    def getGainStages(self):  # Nope, these won't work!?
#        return ["RFGR", "IFGR"]

    def getInputs(self) -> List[Input]:
        return super().getInputs() + [
            BiasTeeInput(),
            CheckboxInput(
                "offset_tune",
                "Enable Offset Tuning Mode",
            ),
            DropdownInput(
                "bufflen",
                "Buffer Length",
                BuffLenOptions,
            ),
        ]

    def getDeviceOptionalKeys(self):
        return super().getDeviceOptionalKeys() + ["bias_tee", "offset_tune", "bufflen"]

    def getProfileOptionalKeys(self):
        return super().getProfileOptionalKeys() + ["bias_tee", "offset_tune", "bufflen"]

