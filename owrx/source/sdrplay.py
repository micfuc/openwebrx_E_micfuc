from owrx.source.soapy import SoapyConnectorSource, SoapyConnectorDeviceDescription
from owrx.form.input import Input, CheckboxInput, DropdownInput, NumberInput, DropdownEnum
from owrx.form.input.device import BiasTeeInput, GainInput
from owrx.form.input.validator import RangeValidator
from typing import List


class SdrplaySource(SoapyConnectorSource):
    def getSoapySettingsMappings(self):
        mappings = super().getSoapySettingsMappings()
        mappings.update(
            {
                "bias_tee": "biasT_ctrl",
                "rf_notch": "rfnotch_ctrl",
                "dab_notch": "dabnotch_ctrl",
                "if_mode": "if_mode",
                "external_reference": "extref_ctrl",
                "rfgain_sel": "rfgain_sel",
                "agc_setpoint": "agc_setpoint",
            }
        )
        return mappings

    def getDriver(self):
        return "sdrplay"


class IfModeOptions(DropdownEnum):
    IFMODE_ZERO_IF = "Zero-IF"
    IFMODE_450 = "450kHz"
    IFMODE_1620 = "1620kHz"
    IFMODE_2048 = "2048kHz"

    def __str__(self):
        return self.value


class SdrplayDeviceDescription(SoapyConnectorDeviceDescription):
    def getName(self):
        return "SDRPlay device (RSP1, RSP2, RSPDuo, RSPDx)"

    def getInputs(self) -> List[Input]:
        return super().getInputs() + [
            BiasTeeInput(),
            CheckboxInput(
                "rf_notch",
                "Enable RF notch filter",
            ),
            CheckboxInput(
                "dab_notch",
                "Enable DAB notch filter",
            ),
            DropdownInput(
                "if_mode",
                "IF Mode",
                IfModeOptions,
            ),
            NumberInput(
                "rfgain_sel",
                "RF gain reduction",
                validator=RangeValidator(0, 32),
            ),
            NumberInput(
                "agc_setpoint",
                "AGC setpoint",
                append="dBFS",
                validator=RangeValidator(-60, 0),
            ),
            GainInput(
                "rf_gain",
                "IF gain reduction",
                has_agc=self.hasAgc(),
            ),
        ]

    def getDeviceOptionalKeys(self):
        return super().getDeviceOptionalKeys() + ["bias_tee", "rf_notch", "dab_notch", "if_mode", "rfgain_sel", "agc_setpoint"]

    def getProfileOptionalKeys(self):
        return super().getProfileOptionalKeys() + ["bias_tee", "rf_notch", "dab_notch", "if_mode", "rfgain_sel", "agc_setpoint"]
