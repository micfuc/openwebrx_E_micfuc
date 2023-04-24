from owrx.controllers.settings import SettingsFormController
from owrx.form.section import Section
from owrx.config.core import CoreConfig
from owrx.form.input import (
    TextInput,
    NumberInput,
    FloatInput,
    TextAreaInput,
    DropdownInput,
    CheckboxInput,
    Option,
)
from owrx.form.input.validator import RangeValidator
from owrx.form.input.converter import WaterfallColorsConverter, IntConverter
from owrx.form.input.receiverid import ReceiverKeysConverter
from owrx.form.input.gfx import AvatarInput, TopPhotoInput
from owrx.form.input.device import WaterfallLevelsInput, WaterfallAutoLevelsInput
from owrx.form.input.location import LocationInput
from owrx.waterfall import WaterfallOptions
from owrx.breadcrumb import Breadcrumb, BreadcrumbItem
from owrx.controllers.settings import SettingsBreadcrumb
import shutil
import os
import re
from glob import glob

import logging

logger = logging.getLogger(__name__)


class GeneralSettingsController(SettingsFormController):
    def getTitle(self):
        return "General Settings"

    def get_breadcrumb(self) -> Breadcrumb:
        return SettingsBreadcrumb().append(BreadcrumbItem("General Settings", "settings/general"))

    def getSections(self):
        return [
            Section(
                "Receiver information",
                TextInput("receiver_name", "Receiver name"),
                TextInput("receiver_location", "Receiver location"),
                NumberInput(
                    "receiver_asl",
                    "Receiver elevation",
                    append="meters above mean sea level",
                ),
                TextInput("receiver_admin", "Receiver admin"),
                LocationInput("receiver_gps", "Receiver coordinates"),
                TextInput("photo_title", "Photo title"),
                TextAreaInput("photo_desc", "Photo description", infotext="HTML supported "),
            ),
            Section(
                "Receiver images",
                AvatarInput(
                    "receiver_avatar",
                    "Receiver Avatar",
                    infotext="For performance reasons, images are cached. "
                    + "It can take a few hours until they appear on the site.",
                ),
                TopPhotoInput(
                    "receiver_top_photo",
                    "Receiver Panorama",
                    infotext="For performance reasons, images are cached. "
                    + "It can take a few hours until they appear on the site.",
                ),
                DropdownInput(
                    "black_mod",
                    "Black background",
                    infotext="Replace background photo with solid black ",
                    options=[
                        Option("webrx-top-container-black", "Enable"),
                        Option("webrx-top-container", "Disable"),
                    ],
                ),                                
            ),
            Section(
                "Top Bar Panels Toggle Buttons Display ",
                DropdownInput(
                    "status_button",
                    "Status Panel Button Display",
                    infotext="Enable display of Bottom left Status Panel toggle button ",
                    options=[
                        Option("status_but_enable", "Enable"),
                        Option("status_but_disable", "Disable"),
                    ],
                ), 
                DropdownInput(
                    "log_button",
                    "Log Panel Button Display",
                    infotext="Enable display of Bottom left Log panel toggle button ",
                    options=[
                        Option("log_but_enable", "Enable"),
                        Option("log_but_disable", "Disable"),
                    ],
                ),
                DropdownInput(
                    "receiver_button",
                    "Receiver Panel Button Display",
                    infotext="Enable display of Bottom right Receiver Panel toggle button ",
                    options=[
                        Option("receiver_but_enable", "Enable"),
                        Option("receiver_but_disable", "Disable"),
                    ],
                ), 
                DropdownInput(
                    "map_button",
                    "Map Page Button Display",
                    infotext="Direct link to Receiver Map Page Display ",
                    options=[
                        Option("map_but_enable", "Enable"),
                        Option("map_but_disable", "Disable"),
                    ],
                ),
                DropdownInput(             # by I8FUC 20230404
                    "settings_button",
                    "Settings Page Button Display",
                    infotext="Direct link to Receiver Settings Page Display ",
                    options=[
                        Option("settings_but_enable", "Enable"),
                        Option("settings_but_disable", "Disable"),
                    ],
                ),  
                DropdownInput(
                    "files_button",
                    "Files Page Button Display",
                    infotext="Direct link to Files(SSTV) Page Display ",
                    options=[
                        Option("files_but_enable", "Enable"),
                        Option("files_but_disable", "Disable"),
                    ],
                ),                                              
            ),            
            Section(
                "Receiver limits",
                NumberInput(
                    "max_clients",
                    "Maximum number of clients",
                    infotext="Number of people who can connect at the same time.",
                ),
                NumberInput(
                    "keep_files",
                    "Maximum number of files",
                    infotext="Number of received images and other files to keep.",
                ),
                NumberInput(
                    "session_timeout",
                    "Session timeout",
                    infotext="Client session timeout in seconds (0 to disable timeout).",
                    append="secs",
                ),
                TextInput(
                    "usage_policy_url",
                    "Usage policy URL",
                    infotext="Specifies web page describing receiver usage policy "
                    + "and shown when a client session times out.",
                ),
            ),
            Section(
                "Receiver listings",
                TextAreaInput(
                    "receiver_keys",
                    "Receiver keys",
                    converter=ReceiverKeysConverter(),
                    infotext="Put the keys you receive on listing sites (e.g. "
                    + '<a href="https://www.receiverbook.de" target="_blank">Receiverbook</a>) here, one per line',
                ),
            ),
            Section(
                "Admin Mode Tuning Features",
                DropdownInput(
                    "agile_mode",
                    "Agile-Mode profile",
                    infotext="Profile allowing direct center frequency change from main GUI ",
                    options=[
                        Option("agile_but_enable", "Enable"),
                        Option("agile_but_disable", "Disable"),
                    ],
                ),
                DropdownInput(
                    "jumper_mode",
                    "'Jumper' Pseudo scanning mode",
                    infotext="Allows to automagically change a preset number of profiles in sequence with a defined time interval",
                    options=[
                        Option("jumper_but_enable", "Enable"),
                        Option("jumper_but_disable", "Disable"),
                    ]
                ),
            ),
            Section(
                "Waterfall settings",
                DropdownInput(
                    "waterfall_scheme",
                    "Waterfall color scheme",
                    options=WaterfallOptions,
                ),
                TextAreaInput(
                    "waterfall_colors",
                    "Custom waterfall colors",
                    infotext="Please provide 6-digit hexadecimal RGB colors in HTML notation (#RRGGBB)"
                    + " or HEX notation (0xRRGGBB), one per line",
                    converter=WaterfallColorsConverter(),
                ),
                NumberInput(
                    "fft_fps",
                    "FFT speed",
                    infotext="This setting specifies how many lines are being added to the waterfall per second. "
                    + "Higher values will give you a faster waterfall, but will also use more CPU.",
                    append="frames per second",
                ),
                NumberInput("fft_size", "FFT size", append="bins"),
                FloatInput(
                    "fft_voverlap_factor",
                    "FFT vertical overlap factor",
                    infotext="If fft_voverlap_factor is above 0, multiple FFTs will be used for creating a line on the "
                    + "diagram.",
                ),
                WaterfallLevelsInput("waterfall_levels", "Waterfall levels"),
                WaterfallAutoLevelsInput(
                    "waterfall_auto_levels",
                    "Automatic adjustment margins",
                    infotext="Specifies the upper and lower dynamic headroom that should be added when automatically "
                    + "adjusting waterfall colors",
                ),
                NumberInput(
                    "waterfall_auto_min_range",
                    "Automatic adjustment minimum range",
                    append="dB",
                    infotext="Minimum dynamic range the waterfall should cover after automatically adjusting "
                    + "waterfall colors",
                ),
            ),
            Section(
                "Compression",
                DropdownInput(
                    "audio_compression",
                    "Audio compression",
                    options=[
                        Option("adpcm", "ADPCM"),
                        Option("none", "None"),
                    ],
                ),
                DropdownInput(
                    "fft_compression",
                    "Waterfall compression",
                    options=[
                        Option("adpcm", "ADPCM"),
                        Option("none", "None"),
                    ],
                ),
            ),
            Section(
                "Display settings",
                NumberInput(
                    "ui_opacity",
                    "User interface opacity",
                    infotext="Specifies how opaque user interface is, "
                    + "10% for near invisible, 100% for totally solid.",
                    validator=RangeValidator(10, 100),
                    append="%",
                ),
                CheckboxInput(
                    "ui_frame",
                    "Show frame around receiver panel",
                ),
                DropdownInput(
                    "tuning_precision",
                    "Tuning precision",
                    options=[Option(str(i), "{} Hz".format(10 ** i)) for i in range(0, 6)],
                    converter=IntConverter(),
                ),
            ),
            Section(
                "Map settings",
                TextInput(
                    "google_maps_api_key",
                    "Google Maps API key",
                    infotext="Google Maps requires an API key, check out "
                    + '<a href="https://developers.google.com/maps/documentation/embed/get-api-key" target="_blank">'
                    + "their documentation</a> on how to obtain one.",
                ),
                NumberInput(
                    "map_position_retention_time",
                    "Map retention time",
                    infotext="Specifies how log markers / grids will remain visible on the map",
                    append="s",
                ),
                CheckboxInput(
                    "map_ignore_indirect_reports",
                    "Ignore position reports arriving via indirect path",
                ),
                CheckboxInput(
                    "map_prefer_recent_reports",
                    "Prefer more recent position reports to shorter path reports",
                ),
                TextInput(
                    "callsign_url",
                    "Callsign database URL",
                    infotext="Specifies callsign lookup URL, such as QRZ.COM "
                    + "or QRZCQ.COM. Place curly brackers ({}) where callsign "
                    + "is supposed to be.",
                ),
                TextInput(
                    "vessel_url",
                    "Vessel database URL",
                    infotext="Specifies vessel lookup URL, such as VESSELFINDER.COM, "
                    + "allowing to look up vessel information by its AIS MMSI number. "
                    + "Place curly brackers ({}) where MMSI is supposed to be.",
                ),
            ),
        ]

    def remove_existing_image(self, image_id):
        config = CoreConfig()
        # remove all possible file extensions
        for ext in ["png", "jpg", "webp"]:
            try:
                os.unlink("{}/{}.{}".format(config.get_data_directory(), image_id, ext))
            except FileNotFoundError:
                pass

    def handle_image(self, data, image_id):
        if image_id in data:
            config = CoreConfig()
            if data[image_id] == "restore":
                self.remove_existing_image(image_id)
            elif data[image_id]:
                if not data[image_id].startswith(image_id):
                    logger.warning("invalid file name: %s", data[image_id])
                else:
                    # get file extension (at least 3 characters)
                    # should be all lowercase since they are set by the upload script
                    pattern = re.compile(".*\\.([a-z]{3,})$")
                    matches = pattern.match(data[image_id])
                    if matches is None:
                        logger.warning("could not determine file extension for %s", image_id)
                    else:
                        self.remove_existing_image(image_id)
                        ext = matches.group(1)
                        data_file = "{}/{}.{}".format(config.get_data_directory(), image_id, ext)
                        temporary_file = "{}/{}".format(config.get_temporary_directory(), data[image_id])
                        shutil.copy(temporary_file, data_file)
            del data[image_id]
            # remove any accumulated temporary files on save
            for file in glob("{}/{}*".format(config.get_temporary_directory(), image_id)):
                os.unlink(file)

    def processData(self, data):
        # Image handling
        for img in ["receiver_avatar", "receiver_top_photo"]:
            self.handle_image(data, img)
        # special handling for waterfall colors: custom colors only stay in config if custom color scheme is selected
        if "waterfall_scheme" in data:
            scheme = WaterfallOptions(data["waterfall_scheme"])
            if scheme is not WaterfallOptions.CUSTOM and "waterfall_colors" in data:
                data["waterfall_colors"] = None
        super().processData(data)
