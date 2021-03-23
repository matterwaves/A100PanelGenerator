# exec(open("/home/user/repos/kicad-panel-generator/generate-panel.py").read())
import pcbnew
import re
pcb = pcbnew.GetBoard()


footprint_lib="/home/user/repos/flyg-electronics/flyg-electronics-common/footprints/matterwave.pretty"

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

def get_all_component_names():
    return [x.GetReference() for x in pcb.GetModules()]

def get_layers():
    num=0
    name = ""
    layers=[]
    name=pcb.GetLayerName(num)
    while name != "BAD INDEX!":
        layers.append(name)
        num+=1
        name=pcb.GetLayerName(num)
        #print("{} {}".format(num,name))
        if num > 55:
            break
    return layers


def layer_from_name(name):
    return [num for num in range(len(layers)) if layers[num]==name][0]


layers = get_layers()

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

def add_footprint(x,y,name):
    io = pcbnew.PCB_IO()
    footprint = io.FootprintLoad(footprint_lib,name)
    print(footprint)
    pt=pcbnew.wxPoint(x,y)
    footprint.SetPosition(pt)
    pcb.Add(footprint)
    pcbnew.Refresh()


def draw_edges(origin_in=(3,3),hp=10):
    """ hp = "horizontal pitch" in units of 0.2 in
        Using A100 eurorack standard, 3U modules have a height of 128.5mm
    """
    width=mm_to_nm(hp_to_mm(hp))
    height=mm_to_nm(128.5)
    Ox=in_to_nm(origin_in[0])
    Oy=in_to_nm(origin_in[1])

    corners=[(Ox-int(width/2),Oy-int(height/2)),
             (Ox+int(width/2),Oy-int(height/2)),
             (Ox+int(width/2),Oy+int(height/2)),
             (Ox-int(width/2),Oy+int(height/2)),
             ]
    layer=layer_from_name("Edge.Cuts")
    for idx in range(0,4):
        print(idx,(idx+1)%4)
        p1=corners[idx]
        p2=corners[(idx+1)%4]
        print(p1,p2)
        ds=pcbnew.DRAWSEGMENT(pcb)
        pcb.Add(ds)
        ds.SetStart(pcbnew.wxPoint(p1[0],p1[1]))
        ds.SetEnd(  pcbnew.wxPoint(p2[0],p2[1]))
        ds.SetLayer(layer)
    pcbnew.Refresh()


def draw_rail_mount(origin_in=(3,3),hp=10):
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
    name="MountingHole_M3_slot"

    Ox=in_to_nm(origin_in[0])
    Oy=in_to_nm(origin_in[1])
    width=mm_to_nm(hp_to_mm(hp))
    height=mm_to_nm(128.5)
    dy=int(height/2-vert_clear_nm)

    if hp<10:
        hole_centers=[ (Ox,Oy+dy) ,(Ox,Oy-dy)  ]

    else:
        dx=mm_to_nm(5.08*(hp/2-1.5))
        hole_centers=[ (Ox+dx,Oy+dy) ,(Ox+dx,Oy-dy),(Ox-dx,Oy+dy),(Ox-dx,Oy-dy) ]
    for (x,y) in hole_centers:
        add_footprint(x,y,name)






