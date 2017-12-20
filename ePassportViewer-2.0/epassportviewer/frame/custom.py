# Copyright 2012 Antonin Beaujeant
#
# This file is part of epassportviewer.
#
# epassportviewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# epassportviewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with epassportviewer.
# If not, see <http://www.gnu.org/licenses/>.

import os

from Tkinter import *
import tkFont
import tkMessageBox
import Image, ImageTk
from tkFileDialog import askdirectory, askopenfilename, asksaveasfilename

from Crypto.Cipher import DES3
from Crypto.Cipher import DES
from hashlib import sha1

from pypassport import apdu, iso9797, asn1
from pypassport.hexfunctions import hexToHexRep, binToHexRep, hexRepToBin
from pypassport.iso7816 import Iso7816, Iso7816Exception
from pypassport.doc9303 import bac, mrz, securemessaging

from epassportviewer.util import readerAbstract
from epassportviewer.util.image import ImageFactory
from epassportviewer.frame.attacks import ScrollFrame
from epassportviewer.dialog import Tooltip, WaitDialog

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString


###################
#     CUSTOM      #
###################

class CustomFrame(Frame):

    def __init__(self, master, mrz=None):
        Frame.__init__(self, master)

        im = Image.open(ImageFactory().create(ImageFactory().HELP))
        image = ImageTk.PhotoImage(im)

        self._iso7816 = False

        self.mrz = mrz

        title = tkFont.Font(size=12)

        ###############
        ## ANALYZING ##

        self.analyzingFrame = Frame(self, borderwidth=1, relief=GROOVE)
        self.analyzingFrame.pack(fill=BOTH, expand=1)

        analyzingLabel = Label(self.analyzingFrame, text="Analyzing", justify=LEFT, font=title)
        analyzingLabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=W)

        randomButton = Button(self.analyzingFrame, text="Dump randomness", width=13, command=self.dumprnd)
        randomButton.grid(row=1, column=0, padx=5, pady=5)
        Tooltip(parent=randomButton, tip="Generate a string of concatenated random number (Get challenge)\nand store it in a file.")

        nbRNDLabel = Label(self.analyzingFrame, text="Nb of GET Challenge:", justify=LEFT)
        nbRNDLabel.grid(row=1, column=1, padx=5, pady=5, sticky=W)

        self.nbRND = Entry(self.analyzingFrame, width=5)
        self.nbRND.grid(row=1, column=2, padx=5, pady=5, sticky=W)

        #self.rstVar = IntVar()
        #rstCheck = Checkbutton(self.analyzingFrame, text="Reset", variable=self.rstVar)
        #rstCheck.grid(row=1, column=3, padx=5, pady=5, sticky=W)


        #########################
        ## AUTOMATIC FUNCTIONS ##

        self.automaticFrame = Frame(self, borderwidth=1, relief=GROOVE)
        self.automaticFrame.pack(fill=BOTH, expand=1)

        automaticLabel = Label(self.automaticFrame, text="Automatic functions", justify=LEFT, font=title)
        automaticLabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=W)

        initButton = Button(self.automaticFrame, text="Init (select file)", width=13, command=self.init)
        initButton.grid(row=1, column=0, padx=5, pady=5)
        Tooltip(parent=initButton, tip="Initialise the connection by selecting\nthe Application Identifier.")

        resetButton = Button(self.automaticFrame, text="Reset", width=13, command=self.reset)
        resetButton.grid(row=1, column=1, padx=5, pady=5)
        Tooltip(parent=resetButton, tip="Reset the connection.")

        bacButton = Button(self.automaticFrame, text="BAC", width=13, command=self.performBAC)
        bacButton.grid(row=1, column=2, padx=5, pady=5)
        Tooltip(parent=bacButton, tip="Perform a complete BAC.")

        genBACKeysButton = Button(self.automaticFrame, text="Generate BAC keys", width=13, command=self.genBACKeys)
        genBACKeysButton.grid(row=1, column=3, padx=5, pady=5)
        Tooltip(parent=genBACKeysButton, tip="Derive Kenc and Kmac for the BAC\nbased on the MRZ set above.")

        getATRButton = Button(self.automaticFrame, text="Get ATR", width=6, command=self.getATR)
        getATRButton.grid(row=1, column=4, padx=5, pady=5)
        Tooltip(parent=genBACKeysButton, tip="Get the Answer to Reset.")


        ###########
        ## TOOLS ##

        self.toolsFrame = Frame(self, borderwidth=1, relief=GROOVE)
        self.toolsFrame.pack(fill=BOTH, expand=1)

        buttonToolsFrame = Frame(self.toolsFrame)
        buttonToolsFrame.pack(fill=BOTH, expand=1)

        toolsLabel = Label(buttonToolsFrame, text="Tools", justify=LEFT, font=title)
        toolsLabel.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=W)

        # CRYPTO
        cryptoLabel = Label(buttonToolsFrame, text="Crypto:", justify=LEFT)
        cryptoLabel.grid(row=1, column=0, padx=5, pady=5, sticky=W)

        tdesEncryptionButton = Button(buttonToolsFrame, text="3DES >", width=10, command=self.tdesEncrypt)
        tdesEncryptionButton.grid(row=1, column=1, pady=5)
        Tooltip(parent=tdesEncryptionButton, tip="Encrypt in 3DES the hex value in the 1st field\nwith the key encryption in the 2nd field.")

        tdesDecryptionButton = Button(buttonToolsFrame, text="3DES <", width=10, command=self.tdesDecrypt)
        tdesDecryptionButton.grid(row=1, column=3, padx=5, pady=5)
        Tooltip(parent=tdesDecryptionButton, tip="Decrypt the 3DES cipher hex value in the 1st field\nwith the key encryption in the 2nd field.")

        sha1EncryptionButton = Button(buttonToolsFrame, text="SHA-1", width=10, command=self.sha1Hash)
        sha1EncryptionButton.grid(row=1, column=4, padx=5, pady=5)
        Tooltip(parent=sha1EncryptionButton, tip="Hash with SHA-1 algorithm\nthe value in the 1st field.")

        createMACButton = Button(buttonToolsFrame, text="Create MAC", width=10, command=self.createMAC)
        createMACButton.grid(row=1, column=5, padx=5, pady=5)
        Tooltip(parent=createMACButton, tip="Create the message authentication code of\nthe cipher in the 1st field  with the Kmac\nin the 2nd field.")


        # FUNCTIONS
        functionsLabel = Label(buttonToolsFrame, text="Functions:", justify=LEFT)
        functionsLabel.grid(row=2, column=0, padx=5, pady=5, sticky=W)

        xorButton = Button(buttonToolsFrame, text="XOR", width=10, command=self.xor)
        xorButton.grid(row=2, column=1, pady=5)
        Tooltip(parent=xorButton, tip="XOR the hex value of the 1st field\nwith the value of the 2nd field.")

        keyDerivationButton = Button(buttonToolsFrame, text="Key  derivation", width=10, command=self.keyDerivation)
        keyDerivationButton.grid(row=2, column=3, padx=5, pady=5)
        Tooltip(parent=keyDerivationButton, tip="Derive the session keys such as:\nK = 16 msb of SHA-1(Kseed||0000000[1,2])\nwhere Kseed is the 1st field and 0000000[1,2]\nis the 2nd field.")

        sscGeneratorButton = Button(buttonToolsFrame, text="SSC generator", width=10, command=self.sscGenerator)
        sscGeneratorButton.grid(row=2, column=4, padx=5, pady=5)
        Tooltip(parent=sscGeneratorButton, tip="Compute the SSC such as:\nSSC = 4 lsb of RND.ICC || 4 lsb RND.IFD\nRND.ICC is in the 1st field and RND.IFD\nis in the 2nd field.")

        readHeaderButton = Button(buttonToolsFrame, text="Read header", width=10, command=self.readHeader)
        readHeaderButton.grid(row=2, column=5, padx=5, pady=5)
        Tooltip(parent=readHeaderButton, tip="Read the first bytes of an EF (header)\nand return the header's size and the\nEF size.")

        self.update()


        # FIELDS
        fieldsFrame = Frame(self.toolsFrame)
        fieldsFrame.pack(fill=BOTH, expand=1)

        fieldsLabel = Label(fieldsFrame, text="Fields:           HEX:", justify=LEFT)
        fieldsLabel.pack(side=LEFT, pady=5)

        self.field1Form = Entry(fieldsFrame, width=32)
        self.field1Form.pack(side=LEFT, pady=5)

        hexLabel = Label(fieldsFrame, text="   HEX:", justify=LEFT)
        hexLabel.pack(side=LEFT, pady=5)

        self.field2Form = Entry(fieldsFrame, width=32)
        self.field2Form.pack(side=LEFT, pady=5)


        ##############
        ## REQUESTS ##

        self.requestsFrame = Frame(self, borderwidth=1, relief=GROOVE)
        self.requestsFrame.pack(fill=BOTH, expand=1)

        # MENU
        menuRequestsFrame = Frame(self.requestsFrame)
        menuRequestsFrame.pack(fill=BOTH, expand=1)

        requestsLabel = Label(menuRequestsFrame, text="Requests", justify=LEFT, font=title)
        requestsLabel.grid(row=0, column=0, padx=5, pady=5, sticky=W)


        externalAuthButton = Button(menuRequestsFrame, text="External Auth.", width=13, command=self.setExternalAuth)
        externalAuthButton.grid(row=1, column=0, padx=5, pady=5)

        internalAuthButton = Button(menuRequestsFrame, text="Internal Auth.", width=13, command=self.setInternalAuth)
        internalAuthButton.grid(row=1, column=1, padx=5, pady=5)

        selectFileButton = Button(menuRequestsFrame, text="Select file", width=13, command=self.setSelectFile)
        selectFileButton.grid(row=1, column=2, padx=5, pady=5)

        readBinaryButton = Button(menuRequestsFrame, text="Read binary", width=13, command=self.setReadBinary)
        readBinaryButton.grid(row=1, column=3, padx=5, pady=5)

        reabilitateButton = Button(menuRequestsFrame, text="Rehabilitate", width=13, command=self.setRehabilitate)
        reabilitateButton.grid(row=1, column=4, padx=5, pady=5)


        getUIDButton = Button(menuRequestsFrame, text="Get UID", width=13, command=self.setGetUID)
        getUIDButton.grid(row=2, column=0, padx=5, pady=5)

        getATSButton = Button(menuRequestsFrame, text="Get ATS", width=13, command=self.setGetATS)
        getATSButton.grid(row=2, column=1, padx=5, pady=5)

        getchallengeButton = Button(menuRequestsFrame, text="Get challenge", width=13, command=self.setGetChallenge)
        getchallengeButton.grid(row=2, column=2, padx=5, pady=5)



        # APDU
        apduFrame = Frame(self.requestsFrame)
        apduFrame.pack(fill=BOTH, expand=1)

        customCLALabel = Label(apduFrame, text="CLA:", justify=LEFT)
        customCLALabel.pack(side=LEFT, padx=5, pady=5)

        self.customCLAForm = Entry(apduFrame, width=2)
        self.customCLAForm.pack(side=LEFT, pady=5)
        self.customCLAForm.insert(0, "00")

        customINSLabel = Label(apduFrame, text="INS:", justify=LEFT)
        customINSLabel.pack(side=LEFT, padx=5, pady=5)

        self.customINSForm = Entry(apduFrame, width=2)
        self.customINSForm.pack(side=LEFT, pady=5)
        self.customINSForm.insert(0, "00")

        customP1Label = Label(apduFrame, text="P1:", justify=LEFT)
        customP1Label.pack(side=LEFT, padx=5, pady=5)

        self.customP1Form = Entry(apduFrame, width=2)
        self.customP1Form.pack(side=LEFT, pady=5)
        self.customP1Form.insert(0, "00")

        customP2Label = Label(apduFrame, text="P2:", justify=LEFT)
        customP2Label.pack(side=LEFT, padx=5, pady=5)

        self.customP2Form = Entry(apduFrame, width=2)
        self.customP2Form.pack(side=LEFT, pady=5)
        self.customP2Form.insert(0, "00")

        customLCLabel = Label(apduFrame, text="LC:", justify=LEFT)
        customLCLabel.pack(side=LEFT, padx=5, pady=5)

        self.customLCForm = Entry(apduFrame, width=2)
        self.customLCForm.pack(side=LEFT, pady=5)

        customDATALabel = Label(apduFrame, text="DATA:", justify=LEFT)
        customDATALabel.pack(side=LEFT, padx=5, pady=5)

        self.customDATAForm = Entry(apduFrame, width=12)
        self.customDATAForm.pack(side=LEFT, pady=5)

        customLELabel = Label(apduFrame, text="LE:", justify=LEFT)
        customLELabel.pack(side=LEFT, padx=5, pady=5)

        self.customLEForm = Entry(apduFrame, width=2)
        self.customLEForm.pack(side=LEFT, pady=5)
        self.customLEForm.insert(0, "00")

        sendCustomButton = Button(apduFrame, text="Send custom APDU", width=13, command=self.send)
        sendCustomButton.pack(side=LEFT, padx=5, pady=5)

        # Ciphering
        cipheringFrame = Frame(self.requestsFrame)
        cipheringFrame.pack(fill=BOTH, expand=1)

        setCipheringButton = Button(cipheringFrame, text="Set ciphering", command=self.setCiphering)
        setCipheringButton.pack(side=LEFT, padx=5, pady=5)

        customKencLabel = Label(cipheringFrame, text="KSenc:", justify=LEFT)
        customKencLabel.pack(side=LEFT, padx=5, pady=5)

        self.customKencForm = Entry(cipheringFrame, width=15)
        self.customKencForm.pack(side=LEFT, pady=5)

        customKmacLabel = Label(cipheringFrame, text="KSmac:", justify=LEFT)
        customKmacLabel.pack(side=LEFT, padx=5, pady=5)

        self.customKmacForm = Entry(cipheringFrame, width=15)
        self.customKmacForm.pack(side=LEFT, pady=5)

        customSscLabel = Label(cipheringFrame, text="SSC:", justify=LEFT)
        customSscLabel.pack(side=LEFT, padx=5, pady=5)

        self.customSscForm = Entry(cipheringFrame, width=10)
        self.customSscForm.pack(side=LEFT, pady=5)



        ##############
        ## RESPONSE ##

        self.responseFrame = Frame(self, borderwidth=1, relief=GROOVE)
        self.responseFrame.pack(fill=BOTH, expand=1)

        requestsLabel = Label(self.responseFrame, text="Response", justify=LEFT, font=title)
        requestsLabel.grid(row=0, column=0, padx=5, pady=5, sticky=W, columnspan=4)

        customCLALabel = Label(self.responseFrame, text="APDU:", justify=LEFT)
        customCLALabel.grid(row=1, column=0, padx=5, pady=5, sticky=W)

        self.customRespDataForm = Entry(self.responseFrame, width=30)
        self.customRespDataForm.grid(row=1, column=1, padx=5, pady=5)

        self.customSW1Form = Entry(self.responseFrame, width=4)
        self.customSW1Form.grid(row=1, column=2, padx=5, pady=5)

        self.customSW2Form = Entry(self.responseFrame, width=4)
        self.customSW2Form.grid(row=1, column=3, padx=5, pady=5)

        customINSLabel = Label(self.responseFrame, text="Response data")
        customINSLabel.grid(row=2, column=1, pady=5)

        customINSLabel = Label(self.responseFrame, text="SW1")
        customINSLabel.grid(row=2, column=2, pady=5)

        customINSLabel = Label(self.responseFrame, text="SW2")
        customINSLabel.grid(row=2, column=3, pady=5)


        # LOG
        #logFrame = Frame(self)
        #logFrame.pack(fill=BOTH, expand=1)

        #self.logBox = Text(logFrame, state=NORMAL, height=15, width=92, wrap='none')
        #self.logBox.pack()

        self.logFrame = ScrollFrame(self)
        self.logFrame.pack(fill=BOTH, expand=1)

        # VERBOSE
        verboseFrame = Frame(self)
        verboseFrame.pack(fill=BOTH, expand=1)

        self.verboseVar = IntVar()
        verboseCheck = Checkbutton(verboseFrame, text="Verbose", variable=None)







    #########
    # METHODS
    #########

    def dumprnd(self):
        try:
            formats = [('Raw text','*.bin')]
            fileName = asksaveasfilename(parent=self, filetypes=formats, title="Save as...")
            if self.nbRND.get(): until = int(self.nbRND.get())
            else: until = 200
            pleasewait = WaitDialog(self.mrz)
            pleasewait.setMessage("Please wait until {} GET CHALLENGE\nhave been performed.".format(until))
            if len(fileName) > 0:
                fileName = str(fileName)
                s = fileName.split(os.sep)
                fn = s[-1]
                directory = fileName[0:len(fileName)-len(fn)]
                if os.path.isdir(directory):
                    pleasewait.withdraw()
                    pleasewait.deiconify()
                    pleasewait.update()
                    self.initIso7816()
                    self._iso7816.rstConnection()
                    rndstr = ""
                    i = 0
                    while i < until:
                        rndstr += self._iso7816.getChallenge()
                        #if self.rstVar.get():
                        #    self._iso7816.rstConnection()
                        i += 1

                    with open(fileName, 'wb') as frnd:
                        frnd.write(rndstr)
                    tkMessageBox.showinfo("Save successful", "The randomness has been saved as:\n{0}".format(fileName))
                else:
                    tkMessageBox.showerror("Error: save", "The path you selected is not a directory")
        except Exception, msg:
            tkMessageBox.showerror("Error: Dump randomness", str(msg))
        finally:
            pleasewait.closeDialog()

    def writeToLog(self, msg):
        self.logFrame.insert(END, "{0}\n".format(msg), False)

    def initIso7816(self):
        try:
            if not self._iso7816:
                r = readerAbstract.waitForCard()
                self._iso7816 = Iso7816(r)
        except Exception, msg:
            tkMessageBox.showerror("Error: Initialisation of ISO7816", str(msg))

    def init(self):
        try:
            self.initIso7816()
            self._iso7816.selectFile("04", "0C", "A0000002471001")
            self.writeToLog("INIT:  APDU: CLA:00 INS:A4 P1:04 P2:0C DATA:A0000002471001")
        except Exception, msg:
            tkMessageBox.showerror("Error: Select file init", str(msg))

    def reset(self):
        try:
            self.initIso7816()
            self._iso7816.rstConnectionRaw()
            self._iso7816.setCiphering()
            self.writeToLog("RESET")
        except Exception, msg:
            tkMessageBox.showerror("Error: Reset", str(msg))

    def performBAC(self):
        try:
            if self.mrz.buildMRZ():
                self.reset()
                self.init()
                basic_access_control = bac.BAC(self._iso7816)
                (KSenc, KSmac, ssc) = basic_access_control.authenticationAndEstablishmentOfSessionKeys(mrz.MRZ(self.mrz.buildMRZ()))
                sm = securemessaging.SecureMessaging(KSenc, KSmac, ssc)
                self._iso7816.setCiphering(sm)
                self.writeToLog("CIPHERING SET:\n{0}".format(sm))
            else:
                tkMessageBox.showerror("Error: BAC", "You have to set the proper MRZ first")
        except Exception, msg:
            tkMessageBox.showerror("Error: BAC", str(msg))

    def genBACKeys(self):
        try:
            if self.mrz.buildMRZ():
                basic_access_control = bac.BAC(self._iso7816)
                mrz_to_send = mrz.MRZ(self.mrz.buildMRZ())
                mrz_to_send.checkMRZ()
                (Kenc, Kmac) = basic_access_control.derivationOfDocumentBasicAccesKeys(mrz_to_send)
                Kenc = binToHexRep(Kenc)
                Kmac = binToHexRep(Kmac)
                self.writeToLog("GENERATE THE BAC KEYS:\n  Kenc: {0}\n  Kmac: {1}".format(Kenc, Kmac))
                self.field1Form.delete(0, END)
                self.field1Form.insert(0, Kenc)
                self.field2Form.delete(0, END)
                self.field2Form.insert(0, Kmac)
            else:
                tkMessageBox.showerror("Error: Generate BAC keys", "You have to set the proper MRZ first")
        except Exception, msg:
            tkMessageBox.showerror("Error: BAC", str(msg))

    def tdesEncrypt(self):
        try:
            tdes= DES3.new(hexRepToBin(self.field2Form.get()), DES.MODE_CBC, b'\x00\x00\x00\x00\x00\x00\x00\x00')
            m = tdes.encrypt(hexRepToBin(self.field1Form.get()))

            self.writeToLog("TDES ENCRYPTION:\n  message: {0}\n  key: {1}\n  cipher: {2}".format(self.field1Form.get(),
                                                                                                 self.field2Form.get(),
                                                                                                 binToHexRep(m)))

            self.field1Form.delete(0, END)
            self.field2Form.delete(0, END)
            self.field1Form.insert(0, binToHexRep(m))

        except Exception, msg:
            tkMessageBox.showerror("Error: BAC", str(msg))

    def tdesDecrypt(self):
        try:
            tdes= DES3.new(hexRepToBin(self.field2Form.get()), DES.MODE_CBC, b'\x00\x00\x00\x00\x00\x00\x00\x00')
            m = tdes.decrypt(hexRepToBin(self.field1Form.get()))

            self.writeToLog("TDES DECRYPTION:\n  cipher: {0}\n  key: {1}\n  message: {2}".format(self.field1Form.get(),
                                                                                                 self.field2Form.get(),
                                                                                                 binToHexRep(m)))

            self.field1Form.delete(0, END)
            self.field2Form.delete(0, END)
            self.field1Form.insert(0, binToHexRep(m))

        except Exception, msg:
            tkMessageBox.showerror("Error: BAC", str(msg))

    def sha1Hash(self):
        h = sha1(self.field1Form.get()).digest()

        self.writeToLog("SHA-1 HASH:\n  message: {0}\n  hash: {1}".format(self.field1Form.get(),
                                                                          binToHexRep(h)))

        self.field1Form.delete(0, END)
        self.field2Form.delete(0, END)
        self.field1Form.insert(0, binToHexRep(h))

    def xor(self):
        out = ""
        for i in range(len(self.field1Form.get())):
            out += hex(int(self.field1Form.get()[i],16) ^ int(self.field2Form.get()[i],16))[2:]

        self.writeToLog("XOR:\n  HEX 1: {0}\n  HEX 2: {1}\n  XOR:   {2}".format(self.field1Form.get(),
                                                                          self.field2Form.get(),
                                                                          out.upper()))

        self.field1Form.delete(0, END)
        self.field2Form.delete(0, END)
        self.field1Form.insert(0, out.upper())

    def createMAC(self):
        try:
            m = iso9797.mac(hexRepToBin(self.field2Form.get()), iso9797.pad(hexRepToBin(self.field1Form.get())))

            self.writeToLog("MAC:\n  message: {0}\n  Key: {1}\n  MAC: {2}".format(self.field1Form.get(),
                                                                          self.field2Form.get(),
                                                                          binToHexRep(m)))

            self.field1Form.delete(0, END)
            self.field2Form.delete(0, END)
            self.field1Form.insert(0, binToHexRep(m))
        except Exception, msg:
            tkMessageBox.showerror("Error: BAC", str(msg))

    def keyDerivation(self):

        keyBin = hexRepToBin(self.field1Form.get())
        h = sha1(str(keyBin)).digest()

        Ka = h[:8]
        Kb = h[8:16]

        Ka = self.DESParity(Ka)
        Kb = self.DESParity(Kb)

        key = binToHexRep(Ka+Kb)

        self.writeToLog("KEY DERIVATION:\n  key: {0}\n  derived key: {1}".format(self.field1Form.get(),
                                                                          key))
        self.field1Form.delete(0, END)
        self.field2Form.delete(0, END)
        self.field1Form.insert(0, key)

    def DESParity(self, data):
        adjusted= ''
        for x in range(len(data)):
            y= ord(data[x]) & 0xfe
            parity= 0
            for z in range(8):
                parity += y >>  z & 1
            adjusted += chr(y + (not parity % 2))
        return adjusted

    def sscGenerator(self):
        rnd_icc = hexRepToBin(self.field1Form.get())
        rnd_ifd = hexRepToBin(self.field2Form.get())
        ssc = rnd_icc[-4:] + rnd_ifd[-4:]
        self.writeToLog("SSC GENERATOR:\n  RND ICC: {0}\n  RND IFD: {1}\n  SSC: {2}".format(self.field1Form.get(),
                                                                                            self.field2Form.get(),
                                                                                            binToHexRep(ssc)))

        self.field1Form.delete(0, END)
        self.field2Form.delete(0, END)
        self.field1Form.insert(0, binToHexRep(ssc))

    def readHeader(self):
        try:
            header = hexRepToBin(self.field1Form.get())
            (bodySize, offset) = asn1.asn1Length(header[1:])
            bodySize = hexToHexRep(bodySize)
            offset = hexToHexRep(offset+1)
            self.writeToLog("HEADER:\n  Body size: {0}\n  Offset: {1}".format(bodySize,
                                                                              offset))

            self.field1Form.delete(0, END)
            self.field2Form.delete(0, END)
            self.field1Form.insert(0, bodySize)
            self.field2Form.insert(0, offset)
        except Exception, msg:
            tkMessageBox.showerror("Error: Read header", str(msg))

    def setRequest(self, cla="00", ins="00", p1="00", p2="00", lc="", data="", le="00"):
        self.customCLAForm.delete(0, END)
        self.customCLAForm.insert(0, cla)
        self.customINSForm.delete(0, END)
        self.customINSForm.insert(0, ins)
        self.customP1Form.delete(0, END)
        self.customP1Form.insert(0, p1)
        self.customP2Form.delete(0, END)
        self.customP2Form.insert(0, p2)
        self.customLCForm.delete(0, END)
        self.customLCForm.insert(0, lc)
        self.customDATAForm.delete(0, END)
        self.customDATAForm.insert(0, data)
        self.customLEForm.delete(0, END)
        self.customLEForm.insert(0, le)

    def setExternalAuth(self):
        self.setRequest(ins="82", le="28")

    def setInternalAuth(self):
        self.setRequest(ins="88")

    def setSelectFile(self):
        self.setRequest(ins="A4", p1="02", p2="0C", le="")

    def setReadBinary(self):
        self.setRequest(ins="B0")

    def setRehabilitate(self):
        self.setRequest(ins="44")

    def setGetUID(self):
        self.setRequest(cla="FF", ins="CA", p1="00", p2="00")

    def setGetATS(self):
        self.setRequest(cla="FF", ins="CA", p1="01", p2="00")

    def setGetChallenge(self):
        self.setRequest(ins="84", le="08")


    def send(self):
        try:
            self.initIso7816()

            cla = self.customCLAForm.get()
            ins = self.customINSForm.get()
            p1 = self.customP1Form.get()
            p2 = self.customP2Form.get()
            lc = self.customLCForm.get()
            data = self.customDATAForm.get()
            le = self.customLEForm.get()

            if not lc:
                if data:
                    lc = hexToHexRep(len(data)/2)

            toSend = apdu.CommandAPDU(cla, ins, p1, p2, lc, data, le)

            ans = self._iso7816.transmitRaw(toSend)
            rep = binToHexRep(ans.res)
            sw1 = ans.sw1
            sw2 = ans.sw2
            self.writeToLog("REQUEST:\n  APDU: CLA:{0} INS:{1} P1:{2} P2:{3} LC:{4} DATA:{5} LE:{6}".format(cla, ins, p1, p2, lc, data, le))
            self.writeToLog("RESPONSE:\n  APDU:\n    Data:{0}\n    SW1:{1}\n    SW2:{2}".format(rep, hex(sw1), hex(sw2)))

            self.customRespDataForm.delete(0, END)
            self.customRespDataForm.insert(0, rep)
            self.customSW1Form.delete(0, END)
            self.customSW1Form.insert(0, sw1)
            self.customSW2Form.delete(0, END)
            self.customSW2Form.insert(0, sw2)

        except Exception, msg:
            tkMessageBox.showerror("Error: Send", str(msg))

    def setCiphering(self):
        try:
            self.initIso7816()
            KSenc = hexRepToBin(self.customKencForm.get())
            KSmac = hexRepToBin(self.customKmacForm.get())
            ssc = hexRepToBin(self.customSscForm.get())
            sm = securemessaging.SecureMessaging(KSenc, KSmac, ssc)
            self._iso7816.setCiphering(sm)
            self.writeToLog("CIPHERING SET:\n{0}".format(sm))
        except Exception, msg:
            tkMessageBox.showerror("Error: Set ciphering", str(msg))

    def getATR(self):
        cardtype = AnyCardType()
        cardrequest = CardRequest(timeout=1, cardType=cardtype)
        cardservice = cardrequest.waitforcard()

        cardservice.connection.connect()
        atr = toHexString(cardservice.connection.getATR())
        self.writeToLog("ATR: {0}".format(atr))

