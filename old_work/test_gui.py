import Tkinter
import sys
import Dialog
import tkSimpleDialog
from Tkinter import *
#from wxPython.wx import *

root = Tk()
menubar = Menu(root)
root.config(menu=menubar)


#Create a menu button labeled "File" that brings up a menu 

filemenu = Menu(menubar)
editmenu = Menu(menubar)
viewmenu = Menu(menubar)

menubar.add_cascade(label='File', menu=filemenu)
menubar.add_cascade(label='Edit',menu=editmenu)
menubar.add_cascade(label='View',menu=viewmenu)

# Create entries in the "File" menu
# simulated command functions that we want to invoke from our menus
def doPrint( ): print 'doPrint'
def doSave( ): print 'doSave' 
filemenu.add_command(label='Print', command=doPrint) 
filemenu.add_command(label='Save', command=doSave) 
filemenu.add_separator( ) 
filemenu.add_command(label='Quit', command=sys.exit)

vlevel = IntVar( )
viewmenu.add_radiobutton(label='Level 1', var=vlevel, value=1)
viewmenu.add_radiobutton(label='Level 2', var=vlevel, value=2)
viewmenu.add_radiobutton(label='Level 3', var=vlevel, value=3)

def ask(title, text, strings=('Yes', 'No'), 
bitmap='questhead', default=0):
	d = Dialog.Dialog(
		title=title, text=text, bitmap=bitmap,
default=default, strings=strings) 
	return strings[d.num]

y = ask
print y

x = tkSimpleDialog.askinteger("Choose an integer", "Between 1 and 6 please:",
initialvalue=1, minvalue=1, maxvalue=6)

print x

class MainFrame(wxFrame): 
#
# snipped: mainframe class attributes
#
    def __init__(self, parent, id, title):
	#
	# snipped: frame-specific initialization
        #
	# Create the notebook
	self.nb = wxNotebook(self, -1,
	   wxPoint(0,0), wxSize(0,0), wxNB_FIXEDWIDTH)
	# Populate the notebook with pages (panels)
	panel_names = "First Panel", "Second Panel", "The Third One"
	panel_scripts = "panel1", "panel2", "panel3"
	for name, script in zip(panel_names, panel_scripts):
	    # Make panel named 'name' (driven by script name)
	    self.module = __import__(script, globals( )) 
	    self.window = self.module.runPanel(self, self.nb)
	    if self.window: self.nb.AddPage(self.window,name)

root.mainloop()


