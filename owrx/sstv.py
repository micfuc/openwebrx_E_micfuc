from owrx.storage import Storage
from csdr.module import ThreadModule
from pycsdr.types import Format
from datetime import datetime
import base64
import pickle
import os

import logging

logger = logging.getLogger(__name__)

modeNames = {
    8:  "Robot 36",
    12: "Robot 72",
    40: "Martin 2",
    44: "Martin 1",
    56: "Scottie 2",
    60: "Scottie 1",
    75: "Scottie DX",

    # Unsupported modes
    0:  "Robot 12",
    1:  "Robot 12",
    2:  "Robot 12",
    3:  "Robot BW8",
    4:  "Robot 24",
    5:  "Robot 24",
    6:  "Robot 24",
    7:  "Robot BW12",
    9:  "Robot BW12",
    10: "Robot BW12",
    11: "Robot BW24",
    13: "Robot BW24",
    14: "Robot BW24",
    15: "Robot BW36",
    32: "Martin M4",
    36: "Martin M3",
    41: "Martin HQ1",
    42: "Martin HQ2",
    48: "Scottie 4",
    52: "Scottie 3",
    85: "FAX480",
    90: "FAST FM",
    93: "PD 50",
    95: "PD 120",
    96: "PD 180",
    97: "PD 240",
    98: "PD 160",
    99: "PD 90",
    100: "Proskan J120",
    104: "MSCAN TV-1",
    105: "MSCAN TV-2",
    113: "Pasokon P3",
    114: "Pasokon P5",
    115: "Pasokon P7",
}

class SstvParser(ThreadModule):
    def __init__(self, service: bool = False):
        self.service   = service
        self.frequency = 0
        self.file      = None
        self.data      = bytearray(b'')
        self.width     = 0
        self.height    = 0
        self.line      = 0
        self.mode      = 0
        super().__init__()

    def __del__(self):
        # Close currently open file, if any
        self.closeFile()

    def closeFile(self):
        if self.file is not None:
            try:
                logger.debug("Closing bitmap file '%s'." % self.fileName)
                self.file.close()
                self.file = None
                if self.height==0 or self.line<self.height:
                    logger.debug("Deleting short bitmap file '%s'." % self.fileName)
                    os.unlink(self.fileName)
                else:
                    # Delete excessive files from storage
                    logger.debug("Performing storage cleanup...")
                    Storage().cleanStoredFiles()

            except Exception as exptn:
                logger.debug("Exception closing file: %s" % str(exptn))
                self.file = None

    def newFile(self, fileName):
        self.closeFile()
        try:
            self.fileName = Storage().getFilePath(fileName + ".bmp")
            logger.debug("Opening bitmap file '%s'..." % self.fileName)
            self.file = open(self.fileName, "wb")

        except Exception as exptn:
            logger.debug("Exception opening file: %s" % str(exptn))
            self.file = None

    def writeFile(self, data):
        if self.file is not None:
            try:
                self.file.write(data)
            except Exception:
                pass

    def getInputFormat(self) -> Format:
        return Format.CHAR

    def getOutputFormat(self) -> Format:
        return Format.CHAR

    def setDialFrequency(self, frequency: int) -> None:
        self.frequency = frequency

    def run(self):
        logger.debug("%s starting..." % ("Service" if self.service else "Client"))
        # Run while there is input data
        while self.doRun:
            # Read input data
            inp = self.reader.read()
            # Terminate if no input data
            if inp is None:
                logger.debug("%s exiting..." % ("Service" if self.service else "Client"))
                self.doRun = False
                break
            # Add read data to the buffer
            self.data = self.data + inp.tobytes()
            # Process buffer contents
            out = self.process()
            # Keep processing while there is input to parse
            while out is not None:
                self.writer.write(pickle.dumps(out))
                out = self.process()

    def process(self):
        try:
            # Parse bitmap file data (scanlines)
            if self.width>0:
                w = self.width * 3
                if len(self.data)>=w:
                    # Compose result
                    out = {
                        "mode":   "SSTV",
                        "pixels": base64.b64encode(self.data[0:w]).decode(),
                        "line":   self.line,
                        "width":  self.width,
                        "height": self.height
                    }
                    # Advance scanline
                    self.line = self.line + 1
                    # If running as a service...
                    if self.service:
                        # Write a scanline into open image file
                        self.writeFile(self.data[0:w])
                        # Close once the last scanline reached
                        if self.line>=self.height:
                            self.closeFile()
                    # If we reached the end of frame, finish scan
                    if self.line>=self.height:
                        self.width  = 0
                        self.height = 0
                        self.line   = 0
                        self.mode   = 0
                    # Remove parsed data
                    del self.data[0:w]
                    # Return parsed values
                    return out

            # Parse bitmap (BMP) file header starting with 'BM' or debug msgs
            elif len(self.data)>=54:
                # Search for the leading 'BM' or ' ['
                w = self.data.find(b'BM')
                d = self.data.find(b' [')
                # If not found...
                if w<0 and d<0:
                    # Skip all but last character (may have 'B')
                    del self.data[0:len(self.data)-1]
                elif w<0 or (d>=0 and d<w):
                    # Skip everything until ' ['
                    del self.data[0:d]
                    # Look for the closing bracket
                    w = self.data.find(b']')
                    if w>=0:
                        # Extract message contents
                        msg = self.data[2:w].decode()
                        # Remove parsed data
                        del self.data[0:w+1]
                        # Log message
                        logger.debug("%s%s says [%s]" % (
                            ("Service" if self.service else "Client"),
                            ((" at %d" % (self.frequency // 1000)) if self.frequency>0 else ""),
                            msg
                        ))
                        # Return parsed values
                        return {
                            "mode":      "SSTV",
                            "message":   msg,
                            "frequency": self.frequency
                        }
                else:
                    # Skip everything until 'BM'
                    del self.data[0:w]
                    # If got the entire header...
                    if len(self.data)>=54:
                        self.width  = self.data[18] + (self.data[19]<<8) + (self.data[20]<<16) + (self.data[21]<<24)
                        self.height = self.data[22] + (self.data[23]<<8) + (self.data[24]<<16) + (self.data[25]<<24)
                        # BMP height value is negative
                        self.height = 0x100000000 - self.height
                        # SSTV mode is passed via reserved area at offset 6
                        self.mode   = self.data[6]
                        self.line   = 0
                        # Find mode name and time
                        modeName  = modeNames.get(self.mode) if self.mode in modeNames else "Unknown Mode %d" % self.mode
                        timeStamp = datetime.utcnow().strftime("%H:%M:%S")
                        fileName  = Storage().makeFileName("SSTV-{0}", self.frequency)
                        logger.debug("%s receiving %dx%d %s frame as '%s'." % (
                            ("Service" if self.service else "Client"),
                            self.width, self.height, modeName, fileName
                        ))
                        # If running as a service...
                        if self.service:
                            # Create a new image file and write BMP header
                            self.newFile(fileName)
                            self.writeFile(self.data[0:54])
                        # Remove parsed data
                        del self.data[0:54]
                        # Return parsed values
                        return {
                            "mode":      "SSTV",
                            "width":     self.width,
                            "height":    self.height,
                            "sstvMode":  modeName,
                            "timestamp": timeStamp,
                            "filename":  fileName,
                            "frequency": self.frequency
                        }

        except Exception as exptn:
            logger.debug("Exception parsing: %s" % str(exptn))

        # Could not parse input data (yet)
        return None

