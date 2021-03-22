# exec(read("/home/user/repos/kicad-panel-generator/generate-panel.py").open())
import pcbnew
import re
pcb = pcbnew.GetBoard()

#Conversions to/from KiCad format. Yes, I know, there are built-in ones. I discovered those after writing these and haven't refactored.
def mm_to_nm(v):
    return int(v * 1000000)

def nm_to_mm(v):
    return v / 1000000.0

def mil_to_nm(v):
    return v*25400

def nm_to_mil(v):
    return v/25400


def get_all_component_names():
    return [x.GetReference() for x in pcb.GetModules()]

