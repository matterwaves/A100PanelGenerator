# A100 Front Panel Generator

Wouldn't it be great if you could design a PCB in kicad, and then automatically generate a design for a front panel that has all the correct holes in exactly the right places?
Well now you can!

This class is modeled after the A100 Eurorack standard as specified by [Doepfer](http://www.doepfer.de/a100_man/a100m_e.htm).
Feel free to modify it to whatever standard you'd like.

I have it configured for U3 modules, but that is also easy to change.

There isn't any fancy auto-detection of front panel components or anything like that.
It is up to you to modify A100FrontPanel.PANEL_MOUNT_DICT to include key-value pairs that correspond to PCB - Font panel footprints.
For now, all footprints are in the same library, as specified by A100FrontPanel.FOOTPRINT_LIB

For now, it must be run from the python console.
I couldnt get the plugin to register in kicad.

TODO: Parse text elements to generate silkscreen text on front panel 
            
            
        
        
        
## Usage

* Open up the pcb you want to use as a template, `fname.kicad_pcb`
* Open the python console
* `> A100FrontPanel().generatePanel()`
* The script will generate `fname-front-panel.kicad_pcb`, overwriting if it already exists
