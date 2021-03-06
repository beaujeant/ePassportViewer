Changes
=======

From 2.0.6 to 2.1
-----------------

* Clean up the file structure
* Change documentation to Markdown format
* Update the _installation guide_ for Ubuntu 18.08 setup
* Fix PIL > Pillow lib


From 2.0.4c to 2.0.6
--------------------

ePassportViewer > mvc:

* New interface (menu + mrz entry)
* Clear function reset MRZ entry set black BAC in security frame
* Change color for security frame
* Move log menu
* Change configuration menu

ePassportViewer > dialog:

* Fix ABOUT > LICENCE issue
* Delete "OK" buttons
* Clean the "About" interface

ePassportViewer > attacks:

* Add a scroll bar in log

ePassportViewer > custom:

* Add HEX


From 2.0.3 to 2.0.4c
--------------------

ePassportViewer > frame > custom:

* Add the function 'Get ATR'

ePassportViewer > frame > attacks:

* Implementation of the verbose output

pyPassport > attacks > all:

* Fixing clumsy output

pyPassport > Iso7816 & ePassportViewer > frame > custom:

* Add method to get UID

pyPassport > fingerprint & ePassportViewer > mvc & ePassportViewer > dialog:

* Improving the fingerprint method.

ePassportViewer > dialog:

* Add ePassport generator features


From 2.0.2 to 2.0.3
-------------------

pyPassport > iso7816

* Modify rstConnection: set ciphering to False when reseting, which prevent unexpected encryption after reset.

ePassportViewer:

* Add geojasper.

pyPassport > jp2converter:

* Modification for geojasper location. Still clumsy and might raise error, but it makes things work with ePassportViewer.

ePassportViewer > dialog:

* Modify startReading: Handle reading problem because of EAC security.

* Create an dictionnary that append all DG in order to optimize the read of the ePassport for export functions.

ePassportViewer > frame > security:

* Set Active Authentication text in orange if DG15 can't be read.

pypassport > doc9303 > tagconverter:

* Create a new dictionnary to provide more info whenever a DG cannot be read because of EAC for instance.

ePassportViewer > mvc:

* Change menu File ("Save...", "Save as...").
* Improve exports methods (exprotToPDF and exportToXML) making more clear the path handling and optimizing the process.

ePassportViewer > util > inOut:

* Change function toPDF to provide more info

ePassportViewer > util > helper:

* Add new function to output raw dump of the passport


From 2.0.1 to 2.0.2
-------------------

pyPassport > setup.py

* The install didn't browse the sub directory. Now setup.py uses find_packages().

ePassportViewer > frame > attacks:

* Add the new methods addToHistory in order to keep the MRZ in history once used in attacks frame.

ePassportViewer > mvc:

* Improve add/load/save history methods in order to update MRZ added from the attacks frame.

pyPassport > epassport & pyPassport > attacks > all:

* Reset the connection before each communication in order to avoid 'Security status not satisfied' issues.


From 2.0 to 2.0.1
-----------------

pyPassport > attacks > bruteForce > BruteForce > offlineExploit:

* The offline brute force attack also checked if the the message decrypted match the nonce sent. Since it is not necessary and it is time consuming, the second verification has been removed.

pyPassport > attacks > bruteForce > BruteForce > initOffline:

* Since the nonce is not required anymore in the offline attack, the method return the message only.

ePassportViewer > ePassportViewer:

* The file is now executable.

ePassportViewer > frame > custom:

* Binary function 'AND', 'OR' and 'NOT' removed since they are not used.

ePassportViewer > frame > attacks:

* Add help dialogs for 'attacks' frame.
* The 'Reader #' is now in the menu. The 'French passport' check box is named 'Reach max'.
* Change the frame style of attacks in order to unify the style.
