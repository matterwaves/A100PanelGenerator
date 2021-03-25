# exec(open("/home/user/repos/kicad-panel-generator/generate-panel.py").read())
import pcbnew
from numpy import floor
import sys
import os
import inspect

#Conversions to/from KiCad format. Yes, I know, there are built-in ones. I discovered those after writing these and haven't refactored.
def mm_to_nm(v):
    return int(v * 1000000)

def nm_to_mm(v):
    return v / 1000000.0

def mil_to_nm(v):
    return int(v*25400)

def nm_to_mil(v):
    return v/25400

def in_to_nm(v):
    return int(v*25.4*1000000)

def mm_to_hp(v):
    """
    guarantees 0.5-1 hp (2.5-5mm) clearance on each side
    always even number
    """
    hp=floor(v/5.08)+2
    return hp+hp%2
def hp_to_mm(hp):
    """
    A100 module width standards
    values are in mm
    """
    if hp == 1:
        return 5.00
    elif hp == 2:
        return 7.5
    elif hp == 4:
        return 20.0
    elif hp == 6:
        return 30.0
    elif hp == 8:
        return 40.30
    elif hp == 10:
        return 50.50
    elif hp == 12:
        return 60.60
    elif hp == 14:
        return 70.80
    elif hp == 16:
        return 80.90
    elif hp == 18:
        return 91.30
    elif hp == 20:
        return 101.30
    elif hp == 22:
        return 111.40
    elif hp == 28:
        return 141.90
    elif hp == 42:
        return 213.00



class A100FrontPanel(pcbnew.ActionPlugin):
    U3_HEIGHT_MM=128.5
    MAX_PCB_HEIGHT_MM=112
    RAIL_MOUNT_FOOTPRINT="MountingHole_M3_slot"
    FOOTPRINT_LIB="/home/user/repos/flyg-electronics/flyg-electronics-common/footprints/matterwave.pretty"
    #Component : front panel pairs
    #Must be manually updated here
    PANEL_MOUNT_DICT={'RJ45':"MountingHole_RJ45",
                'sma_CONSMA008G':"MountingHole_3.5mm",
                'pot_bourns_PTV09':"MountingHole_7.0mm_PTV09",
                'spdt_M_NKK':"MountingHole_3.5mm",
                'PlaceHolder_voltmeter':"MountingHole_voltmeter"}

    def __init__(self,fname=None):
        if fname == None:
            self.pcb = pcbnew.GetBoard()
        else:
            self.pcb=pcbnew.LoadBoard(fname)
        # Create new pcb layout with suffix "front-panel"
        self.panelFname=self.pcb.GetFileName().split(".kicad_pcb")[0]+"-front-panel.kicad_pcb"
        with open(self.pcb.GetFileName(),"r") as f:
            firstLine=f.readline()+")"
        #"x" --> No overwrite
        #"w" --> Overwrite
        with open(self.panelFname,"w") as f:
            f.write(firstLine)
        self.fp=pcbnew.LoadBoard(self.panelFname)
        self.getDimensions()

    def getDimensions(self):
        # Use pcb border to generate front panel border
        bbox=self.pcb.GetBoardEdgesBoundingBox()
        self.origin=bbox.Centre()
        self.pcbWidth=bbox.GetWidth()
        self.pcbHeight=bbox.GetHeight()
        self.hp=mm_to_hp(nm_to_mm(self.pcbWidth))
        self.fpWidth=mm_to_nm(hp_to_mm(self.hp))
        self.fpHeight=mm_to_nm(A100FrontPanel.U3_HEIGHT_MM)
        print("Board width: {} mm, --> {} hp panel with {} mm clearance/side ".format(self.pcbWidth/1e6,self.hp,(self.hp*5.08-self.pcbWidth/1e6)/2))
        print("Board height: {} mm --> {} mm clearance on top and bottom".format(self.pcbHeight/1e6,(A100FrontPanel.MAX_PCB_HEIGHT_MM-self.pcbHeight/1e6)/2))
        print("Board Center: {} nm".format(self.origin))

    def placeFootprint(self,pt,orientation,name):
        io = pcbnew.PCB_IO()
        footprint = io.FootprintLoad(A100FrontPanel.FOOTPRINT_LIB,name)
        footprint.SetPosition(pt)
        footprint.SetOrientationDegrees(orientation)
        self.fp.Add(footprint)
        #pcbnew.Refresh()

    def drawEdges(self):
        (Ox,Oy)=self.origin

        corners=[pcbnew.wxPoint(Ox-int(self.fpWidth/2),Oy-int(self.fpHeight/2)),
                 pcbnew.wxPoint(Ox+int(self.fpWidth/2),Oy-int(self.fpHeight/2)),
                 pcbnew.wxPoint(Ox+int(self.fpWidth/2),Oy+int(self.fpHeight/2)),
                 pcbnew.wxPoint(Ox-int(self.fpWidth/2),Oy+int(self.fpHeight/2)),
                 ]
        cycled=corners[1:]+corners[:1:]
        for (start,end) in zip(corners,cycled):
            ds=pcbnew.DRAWSEGMENT(self.fp)
            self.fp.Add(ds)
            ds.SetStart(start)
            ds.SetEnd(end)
            ds.SetLayer(pcbnew.Edge_Cuts)


    def railMounts(self):
        """
        A100 standard
        3mm vertical clearance
        1.5hp ~7.5mm horizontal clearance
        2 holes for hp<10
        4 holes for hp>=10

        mounting holes are for M3 screws
            3.2mm diameter

        DEVIATION FROM STANDARD:
            For hp<10, keep mounting holes centered
        """
        vert_clear_nm=mm_to_nm(3)
        (Ox,Oy)=self.origin

        dy=int(self.fpHeight/2-vert_clear_nm)

        if self.hp<10:
            hole_centers=[ (Ox,Oy+dy) ,(Ox,Oy-dy)  ]

        else:
            dx=mm_to_nm(5.08*(self.hp/2-1.5))
            hole_centers=[ (Ox+dx,Oy+dy) ,(Ox+dx,Oy-dy),(Ox-dx,Oy+dy),(Ox-dx,Oy-dy) ]
        for (x,y) in hole_centers:
            pt=pcbnew.wxPoint(x,y)
            self.placeFootprint(pt,0,A100FrontPanel.RAIL_MOUNT_FOOTPRINT)

    def fullZone(self,layer):
        """
        Define a full copper pour on the front panel
        """
        bbox=self.fp.GetBoardEdgesBoundingBox()
        sp = pcbnew.SHAPE_POLY_SET()
        sp.NewOutline()
        sp.Append(bbox.GetLeft() ,bbox.GetTop())
        sp.Append(bbox.GetRight(),bbox.GetTop())
        sp.Append(bbox.GetRight() ,bbox.GetBottom())
        sp.Append(bbox.GetLeft(),bbox.GetBottom())
        # sp.OutlineCount()
        sp.thisown = 0
        zone = pcbnew.ZONE_CONTAINER(self.fp)
        zone.SetOutline(sp)
        zone.SetLayer(layer)
        zone.thisown = 0
        self.fp.Add(zone)

    def componentMounts(self):
        ## Make mounting holes for panel mount components
        mountingHoles=[]
        for module in self.pcb.GetModules():
            componentName=str(module.GetFPID().GetLibItemName())
            if componentName in A100FrontPanel.PANEL_MOUNT_DICT.keys():
                print(componentName,module.GetCenter())
                self.placeFootprint(module.GetCenter(),module.GetOrientationDegrees(),A100FrontPanel.PANEL_MOUNT_DICT[componentName])

        for module in self.fp.GetModules():
            ## Manually add square edge cuts for certain components
            ## Rectangular holes are not possible in library footprint
            ## Copy graphical elements from Dwgs.User to Edge.Cuts
            if str(module.GetFPID().GetLibItemName()) in ["MountingHole_RJ45", "MountingHole_voltmeter"]:
                for graphic in module.GraphicalItemsList():
                   if graphic.GetLayerName() == "Dwgs.User":
                       graphic.SetLayer(pcbnew.Edge_Cuts)


    def generatePanel(self):
        """
        run this on the real circuit to
        extract information needed for generating front panel
        """
        self.getDimensions()
        self.drawEdges()
        self.railMounts()
        self.componentMounts()
        ## Make copper pour for front and back layers
        self.fullZone(pcbnew.F_Cu)
        self.fullZone(pcbnew.B_Cu)
        ## save new front panel file
        self.fp.Save(self.panelFname)
        return

    def Run(self):
        self.generatePanel()
    def defaults(self):
        self.name = "A100 panel generator"
        self.category = "Modify PCB"
        self.description = "generate front panel from pcb layout"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./test.png")
        self.show_toolbar_button = False
    def testRegister(self):
        self.__plugin_path = inspect.getfile(self.__class__)


#A100FrontPanel().register()

#if __name__ == '__main__':
#    if len(sys.argv) < 2:
#        print("Usage: %s <KiCad pcb filename>" % sys.argv[0])
#    else:
#        A100FrontPanel(sys.argv[1]).generatePanel()









