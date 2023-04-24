from owrx.storage import Storage
from csdr.module import ThreadModule
from pycsdr.types import Format
from datetime import datetime
import base64
import pickle
import os

import logging

logger = logging.getLogger(__name__)

class FaxParser(ThreadModule):
    def __init__(self, service: bool = False):
        self.service   = service
        self.frequency = 0
        self.file      = None
        self.data      = bytearray(b'')
        self.width     = 0
        self.height    = 0
        self.depth     = 0
        self.line      = 0
        self.ioc       = 0
        self.lpm       = 0
        self.colors    = None
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
        # No result yet
        out = None

        try:
            # Parse bitmap file data (scanlines)
            if self.width>0:
                b = self.depth / 8 if self.depth>8 else 1
                w = self.width
                if len(self.data)>=w*b:
                    #logger.debug("LINE %d: Got %d/%d pixels" % (self.line, w, len(self.data)/b))
                    # Advance scanline
                    self.line = self.line + 1
                    # If running as a service...
                    if self.service:
                        # Write a scanline into open image file
                        self.writeFile(self.data[0:w*b])
                        # Close once the last scanline reached
                        if self.line>=self.height:
                            self.closeFile()
                    else:
                        # Compose result
                        out = {
                            "mode":   "Fax",
                            "pixels": base64.b64encode(self.data[0:w]).decode(),
                            "line":   self.line-1,
                            "width":  self.width,
                            "height": self.height,
                            "depth":  self.depth
                        }
                    # If we reached the end of frame, finish scan
                    if self.line>=self.height:
                        self.width  = 0
                        self.height = 0
                        self.depth  = 0
                        self.line   = 0
                        self.ioc    = 0
                        self.lpm    = 0
                        self.colors = None
                    # Remove parsed data
                    del self.data[0:w*b]

            # Parse bitmap (BMP) file header starting with 'BM' or debug msgs
            elif len(self.data)>=54+4*256:
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
                        # If not running as a service, compose result
                        if not service:
                            out = {
                                "mode":      "Fax",
                                "message":   msg,
                                "frequency": self.frequency
                            }
                else:
                    # Skip everything until 'BM'
                    del self.data[0:w]
                    # If got the entire header...
                    if len(self.data)>=54+4*256:
                        self.width  = self.data[18] + (self.data[19]<<8) + (self.data[20]<<16) + (self.data[21]<<24)
                        self.height = self.data[22] + (self.data[23]<<8) + (self.data[24]<<16) + (self.data[25]<<24)
                        self.depth  = self.data[28] + (self.data[29]<<8)
                        # BMP height value is negative
                        self.height = 0x100000000 - self.height
                        # Fax mode is passed via reserved area at offset 6
                        self.ioc    = self.data[6] * 4
                        self.lpm    = self.data[7]
                        self.line   = 0
                        # Find total header size
                        headerSize  = 54 + (4*256 if self.depth==8 else 0)
                        # 256x4 palette follows the header
                        if headerSize>54:
                            self.colors = self.data[54:headerSize]
                        else:
                            self.colors = None
                        # Find mode name and time
                        modeName  = "IOC-%d %dLPM" % (self.ioc, self.lpm)
                        timeStamp = datetime.utcnow().strftime("%H:%M:%S")
                        fileName  = Storage().makeFileName("FAX-{0}", self.frequency)
                        logger.debug("%s receiving %dx%d %s frame as '%s'." % (
                            ("Service" if self.service else "Client"),
                            self.width, self.height, modeName, fileName
                        ))
                        # If running as a service...
                        if self.service:
                            # Create a new image file and write BMP header
                            self.newFile(fileName)
                            self.writeFile(self.data[0:headerSize])
                        else:
                            # Compose result
                            out = {
                                "mode":      "Fax",
                                "width":     self.width,
                                "height":    self.height,
                                "depth":     self.depth,
                                "faxMode":   modeName,
                                "timestamp": timeStamp,
                                "filename":  fileName,
                                "frequency": self.frequency
                            }
                        # Remove parsed data
                        del self.data[0:headerSize]

        except Exception as exptn:
            logger.debug("Exception parsing: %s" % str(exptn))

        # Return parsed result or None if no result yet
        return out

