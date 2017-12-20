# Copyright 2012 Jean-Francois Houzard, Olivier Roger, Antonin Beaujeant
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

from Tkinter import *
import tkMessageBox
import Image, ImageTk, tkFont

from string import replace

from epassportviewer.dialog import Tooltip
from epassportviewer.frame import security
from epassportviewer.const import *
from epassportviewer.util.configManager import configManager
from epassportviewer.util.image import convertImage, ImageFactory
from epassportviewer.util.helper import getItem

class Overview(Frame):

    IMAGE, SIGN = xrange(2)

    def __init__(self, master, callback):
        Frame.__init__(self, master, relief=GROOVE, bd=2)

        self.master = master
        self.callback = callback

        self.createLayout()

    def createLayout(self):
        container = Frame(self.master, relief=FLAT, bd=1)
        container.pack(side=TOP, fill=BOTH, expand=True)

        ##########
        ## MENU ##

        menuContainer = Frame(container)
        menuContainer.pack(side=LEFT, fill=Y)

        imRead = Image.open(ImageFactory().create(ImageFactory().READ))
        imageRead = ImageTk.PhotoImage(imRead)

        self.readButton = Button(menuContainer, image=imageRead, command=self.callback.process)
        self.readButton.image = imageRead
        self.readButton.pack(side=TOP, padx=3, pady=8)
        Tooltip(parent=self.readButton, tip="Read the passport")

        imAdditional = Image.open(ImageFactory().create(ImageFactory().ADDITIONAL))
        imageAdditional = ImageTk.PhotoImage(imAdditional)

        self.additionalButton = Button(menuContainer, image=imageAdditional, command=self.callback.AdditionalData, state=DISABLED)
        self.additionalButton.image = imageAdditional
        self.additionalButton.pack(side=TOP, padx=3)
        Tooltip(parent=self.additionalButton, tip="Get the entire content")

        imLog = Image.open(ImageFactory().create(ImageFactory().LOG))
        imageLog = ImageTk.PhotoImage(imLog)

        self.logButton = Button(menuContainer, image=imageLog, command=self.callback.openLog, state=DISABLED)
        self.logButton.image = imageLog
        self.logButton.pack(side=BOTTOM, padx=3, pady=8)
        Tooltip(parent=self.logButton, tip="Read the logs")


        ###################
        ## PROFILE PHOTO ##
        self.Image = Label(container)
        self.Image.pack(side=LEFT, pady=8, padx=10, anchor=N)

        im = Image.open( ImageFactory().create(ImageFactory().NOPICTURE) )
        Tkimage = ImageTk.PhotoImage(im)
        self.Image.config(image=Tkimage)


        ###################
        ## PERSONAL INFO ##

        dataContainer = Frame(container)
        dataContainer.pack(side=LEFT, fill=Y, padx=5, pady=5)

        titleFont = tkFont.Font(family="Helvetica", size=10)
        font = tkFont.Font(family="Helvetica", weight='bold', size=11)
        mrzFont = tkFont.Font(family='courier', size=14)

        self.fields = fields = {}
        fields['type'] = StringVar()
        fields['type'].set("N/A")
        fields['issueCountry'] = StringVar()
        fields['issueCountry'].set("N/A")
        fields['passportNumber'] = StringVar()
        fields['passportNumber'].set("N/A")
        fields['name'] = StringVar()
        fields['name'].set("N/A")
        fields['surname'] = StringVar()
        fields['surname'].set("N/A")
        fields['nationality'] = StringVar()
        fields['nationality'].set("N/A")
        fields['sex'] = StringVar()
        fields['sex'].set("N/A")
        fields['birthDate'] = StringVar()
        fields['birthDate'].set("N/A")
        fields['birthPlace'] = StringVar()
        fields['birthPlace'].set("N/A")
        fields['authority'] = StringVar()
        fields['authority'].set("N/A")
        fields['issueDate'] = StringVar()
        fields['issueDate'].set("N/A")
        fields['expiryDate'] = StringVar()
        fields['expiryDate'].set("N/A")
        fields['eyesColour'] = StringVar()
        fields['eyesColour'].set("N/A")
        fields['height'] = StringVar()
        fields['height'].set("N/A")
        fields['residence'] = StringVar()
        fields['residence'].set("N/A")

        fields['mrz'] = StringVar()


        # ROW 0
        row = 0
        Label(dataContainer, text="Type\t\t\t", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=2, sticky=W)
        Label(dataContainer, text="Issuing Country\t\t\t", font=titleFont, fg='blue').grid(row=row, column=2, columnspan=2, sticky=W)
        Label(dataContainer, text="Passport number", font=titleFont, fg='blue').grid(row=row, column=4, columnspan=2, sticky=W)
        row += 1
        Label(dataContainer, textvariable=fields['type'], font=font).grid(row=row, column=0, columnspan=2, sticky=W)
        Label(dataContainer, textvariable=fields['issueCountry'], font=font).grid(row=row, column=2, columnspan=2, sticky=W)
        Label(dataContainer, textvariable=fields['passportNumber'], font=font).grid(row=row, column=4, columnspan=2, sticky=W)

        # ROW 2
        row += 1
        Label(dataContainer, text="Name", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=6, sticky=W)
        row += 1
        Label(dataContainer, textvariable=fields['name'], font=font).grid(row=row, column=0, columnspan=6, sticky=W)

        # ROW 4
        row += 1
        Label(dataContainer, text="Surname", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=6, sticky=W)
        row += 1
        Label(dataContainer, textvariable=fields['surname'], font=font).grid(row=row, column=0, columnspan=6, sticky=W)

        # ROW 6
        row += 1
        Label(dataContainer, text="Nationality", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=6, sticky=W)
        Label(dataContainer, text="Height", font=titleFont, fg='blue').grid(row=row, column=6, columnspan=6, sticky=W)
        row += 1
        Label(dataContainer, textvariable=fields['nationality'], font=font).grid(row=row, column=0, columnspan=6, sticky=W)
        Label(dataContainer, textvariable=fields['height'], font=font).grid(row=row, column=6, columnspan=6, sticky=W)

        # ROW 8
        row += 1
        Label(dataContainer, text="Date of birth", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=6, sticky=W)
        Label(dataContainer, text="Place of birth", font=titleFont, fg='blue').grid(row=row, column=3, columnspan=6, sticky=W)
        Label(dataContainer, text="Colour of eyes", font=titleFont, fg='blue').grid(row=row, column=6, columnspan=6, sticky=W)
        row += 1
        Label(dataContainer, textvariable=fields['birthDate'], font=font).grid(row=row, column=0, columnspan=6, sticky=W)
        Label(dataContainer, textvariable=fields['birthPlace'], font=font).grid(row=row, column=3, columnspan=6, sticky=W)
        Label(dataContainer, textvariable=fields['eyesColour'], font=font).grid(row=row, column=6, columnspan=6, sticky=W)

        # ROW 10
        row += 1
        Label(dataContainer, text="Sex", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=6, sticky=W)
        Label(dataContainer, text="Authority", font=titleFont, fg='blue').grid(row=row, column=3, columnspan=6, sticky=W)
        Label(dataContainer, text="Residence", font=titleFont, fg='blue').grid(row=row, column=6, columnspan=6, sticky=W)
        row += 1
        Label(dataContainer, textvariable=fields['sex'], font=font).grid(row=row, column=0, columnspan=6, sticky=W)
        Label(dataContainer, textvariable=fields['authority'], font=font).grid(row=row, column=3, columnspan=6, sticky=W)
        Label(dataContainer, textvariable=fields['residence'], font=font).grid(row=row, column=6, columnspan=6, sticky=W)

        # ROW 12
        row += 1
        Label(dataContainer, text="Date of issue", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=3, sticky=W)
        Label(dataContainer, text="Signature", font=titleFont, fg='blue').grid(row=row, column=3, columnspan=3, sticky=W)
        row += 1

        self.Sign = Label(dataContainer)
        self.Sign.grid(row=row, rowspan=3, column=3, columnspan=3)

        im = Image.open( ImageFactory().create(ImageFactory().TRANSPARENT) )
        im.thumbnail((200,150))
        Tkimage = ImageTk.PhotoImage(im)

        self.Sign.config(image=Tkimage)
        self.Sign.image = Tkimage

        Label(dataContainer, textvariable=fields['issueDate'], font=font).grid(row=row, column=0, columnspan=6, sticky=W)
        row += 1

        # ROW 14
        Label(dataContainer, text="Date of Expiry", font=titleFont, fg='blue').grid(row=row, column=0, columnspan=3, sticky=W)
        row += 1
        Label(dataContainer, textvariable=fields['expiryDate'], font=font).grid(row=row, column=0, columnspan=3, sticky=W)


        #################
        ## MRZ LOG BOX ##

        mrzContainer = Frame(self.master, bd=2, relief=GROOVE)
        mrzContainer.pack(side=TOP, fill=BOTH, expand=True, anchor=CENTER)
        Label(mrzContainer, textvariable=fields['mrz'], bg='white', font=mrzFont).pack(side=LEFT, fill=BOTH, expand=True)


        ##############
        ## SECURITY ##

        self.security = security.securityFrame(self)
        self.security.pack(side=TOP, fill=BOTH, expand=True, anchor=CENTER)


        ##########
        ## PACK ##

        self.updatePicture( ImageFactory().create(ImageFactory().TRANSPARENT), self.SIGN)
        self.updatePicture( ImageFactory().create(ImageFactory().NOPICTURE), self.IMAGE)

        self.update()

    def updatePicture(self, path, type):
        im=Image.open(path)

        if type == self.SIGN:
            im.thumbnail((180,180))
        if type == self.IMAGE:
            im.thumbnail((275,275))

        Tkimage = ImageTk.PhotoImage(im)
        if type == self.IMAGE:
            self.Image.config(image=Tkimage)
            self.Image.image = Tkimage
        if type == self.SIGN:
            self.Sign.config(image=Tkimage)
            self.Sign.image = Tkimage

    def loadDG1(self, fields, data):
        if data.has_key('5F1F'):
            mrz = data['5F1F']
            mrz = mrz[:44] + "\n" + mrz[44:]
            if len(data['5F1F']) > 88:
                mrz = mrz[:89] + "\n" + mrz[89:]
            fields['mrz'].set(mrz)

        if data.has_key('5F5B'):
            name = (data['5F5B']).split("<<")
            fields['name'].set(getItem(name[0]))
            fields['surname'].set(getItem(name[1]))

        if data.has_key('5F03'):
            fields['type'].set(getItem(data['5F03']))
        if data.has_key('5F28'):
            fields['issueCountry'].set(getItem(data['5F28']))
        if data.has_key('5A'):
            fields['passportNumber'].set(getItem(data['5A']))
        if data.has_key('5F2C'):
            fields['nationality'].set(getItem(data['5F2C']))
        if data.has_key('5F57'):
            fields['birthDate'].set(getItem(data['5F57']))
        if data.has_key('5F35'):
            fields['sex'].set(getItem(data['5F35']))
        if data.has_key('59'):
            fields['expiryDate'].set(getItem("20" + data['59'])) # 20 make a "real" date

    def loadDG2(self, fields, data):
        tag = None
        if data['A1'].has_key('5F2E'): tag = '5F2E'
        elif data['A1'].has_key('7F2E'): tag = '7F2E'
        if tag != None:
            stream = convertImage(data['A1'][tag])
            try:
                self.updatePicture(stream, self.IMAGE)
            except Exception, msg:
                tkMessageBox.showwarning("Image Error", str(msg))

    def loadDG7(self, fields, data):
        if data.has_key('5F43'):
            try:
                stream = convertImage(data['5F43'][0])
                self.updatePicture(stream, self.SIGN)
            except Exception, msg:
                tkMessageBox.showwarning("Image Error", str(msg))

    def loadDG11(self, fields, data):
        if data.has_key("5F2B"):
            fields['birthDate'].set(getItem(data['5F2B']))
        if data.has_key("5F11"):
            fields['birthPlace'].set(getItem(data['5F11']))
        # This DG keep the accents, contrary to the DG1
        # but beware some passports contain an empty or almost empty 5F0E (e.g. BE: 5F0E0120 or 5F0E00)
        if data.has_key("5F0E") and \
           len(data['5F0E']) > len(fields['name'].get()) + len(fields['surname'].get()):
            if "<<" in data['5F0E']:
              tmpname = (data['5F0E']).split("<<")
              fields['name'].set(getItem(tmpname[0]))
              fields['surname'].set(getItem(tmpname[1]))
            else:
              # no specific separator between name(s) and surname(s)
              tmpname = (data['5F0E']).split(" ")
              namewords = len(fields['name'].get().split(" "))
              fields['name'].set(getItem(' '.join(tmpname[:namewords])))
              fields['surname'].set(getItem(' '.join(tmpname[namewords:])))
        # French, nom d'usage, http://fr.wikipedia.org/wiki/Nom_d'usage_en_France
        if data.has_key("A0") and getItem(data['A0'])[0] != '\x02':
            # TODO: some Belgian passports contain
            # 5F0E 00 A0 06020101 5F0F 00
            # is there a better way to discard their A0??
            old = fields['name'].get()
            fields['name'].set(old + ", " + getItem(data['A0']))


    def loadDG12(self, fields, data):
        if data.has_key("5F19"):
            fields['authority'].set(getItem(data['5F19']))
        if data.has_key("5F26"):
            fields['issueDate'].set(getItem(data['5F26']))

    def loadDG13(self, fields, data):
        if data.has_key("9F01"):
            fields['height'].set(getItem(data['9F01']) + " m")
        if data.has_key("9F02"):
            fields['eyesColour'].set(getItem(data['9F02']))
        if data.has_key("9F03"):
            fields['residence'].set(getItem(data['9F03']))

    def loadDG(self, dg, data):
        if dg in ["61", "67", "6B", "6C", "75", "6D"]:
            if dg == "61": self.loadDG1(self.fields, data)
            elif dg == "75": self.loadDG2(self.fields, data)
            elif dg == "67": self.loadDG7(self.fields, data)
            elif dg == "6B": self.loadDG11(self.fields, data)
            elif dg == "6C": self.loadDG12(self.fields, data)
            elif dg == "6D": self.loadDG13(self.fields, data)

        self.update()

    def clear(self):
        self.updatePicture( ImageFactory().create(ImageFactory().NOPICTURE), self.IMAGE)
        self.updatePicture( ImageFactory().create(ImageFactory().TRANSPARENT), self.SIGN)
        self.additionalButton.config(state=DISABLED)
        #self.logButton.config(state=DISABLED)
        for field in self.fields:
            self.fields[field].set("N/A")
        self.fields["mrz"].set("")



