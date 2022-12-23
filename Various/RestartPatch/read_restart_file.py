import struct
import re
import collections

swift_type_count = 7
swift_lock = "i"
with_mpi = False
with_debug = False
default_align = 8
swift_align = 32

typedict = {
    "double": "d",
    "float": "f",
    "long long": "q",
    "timebin_t": "b",
    "integertime_t": "q",
}

structs = {
    "chemistry_part_data": ("", ""),
    "cooling_part_data": ("", ""),
    "feedback_part_data": ("", ""),
    "black_holes_part_data": ("", ""),
    "rt_part_data": ("", ""),
    "timestep_limiter_data": ("bbc", "a b c"),
}

partfile = open("/home/bv7/Programs/swiftsim/src/hydro/Gizmo/MFV/hydro_part.h", "r")
start = 0
teststr = ""
varnames = ""
ifndef = 0
lastidx = 0
placeholders = {}
for line in partfile.readlines():
    if "union" in line:
        print("Can't handle unions!")
    #    exit(1)
    if "{" in line:
        start += 1
        continue
    if "}" in line:
        placeholders["PLACEHOLDER{0:03d}".format(lastidx)] = line.split()[-1].replace(
            ";", "_"
        )
        lastidx += 1
        start -= 1
        continue
    if "#ifdef" in line:
        ifndef += 1
        continue
    if "#endif" in line:
        ifndef -= 1
        continue
    if ";" in line and start > 0 and ifndef == 0:
        pointer = False
        if "*" in line:
            pointer = True
        spacepos = line.rfind(" ")
        vtype, vname = (
            line[:spacepos].strip(),
            line[spacepos:].strip().replace(";", ""),
        )
        if start > 1:
            vname = "PLACEHOLDER{0:03d}{1}".format(lastidx, vname)
        arrays = re.findall("\[(\d+)\]", vname)
        valcount = 1
        if len(arrays) > 0:
            for a in arrays:
                valcount *= int(a)
                vname = vname.replace("[{0}]".format(a), "")
        if pointer:
            vtype = "P"
            vname = vname.replace("*", "")
            vname += "_pointer"
        if "struct" in vtype:
            vtype = vtype.split()[1]
            vname = vtype + "_" + structs[vtype][1]
            vtype = structs[vtype][0]
        if vtype in typedict:
            vtype = typedict[vtype]
        print(vname, vtype, valcount)
        if valcount > 1:
            teststr += "{0}{1}".format(valcount, vtype)
            for i in range(valcount):
                varnames += " {0}_{1}".format(vname, i)
        else:
            teststr += vtype
            if len(vtype) > 0:
                varnames += " {0}".format(vname)
print(teststr, varnames)
for ph in placeholders:
    varnames = varnames.replace(ph, placeholders[ph])

# we skip reading the engine, since it contains too many weird types (e.g. pthread_mutex_t)


def pad_bytes(bytes, align=default_align):
    while struct.calcsize(bytes) % align:
        bytes += "x"
    return bytes


# space
batchstr = "qq"
uniqueidstr = "{0}{0}q{1}".format(batchstr, swift_lock)
spacestr = "3diiiiiiidddddddiiiiiiiiiiPPPPPPPPNNNNNNNNNNNNNNNNNNNNNPPPPPPffffffffff{0}d{0}qff{1}iPP{2}".format(
    swift_type_count, swift_lock, uniqueidstr
)
spaceelements = {"nr_parts": 35}
if with_mpi:
    spacestr += "PNNPNNPNNPNN"
spacestr = pad_bytes(spacestr)

headerstr = "N21s"
headerstr = pad_bytes(headerstr)

integertimetstr = "q"

chemistrystr = ""
coolingstr = ""
feedbackstr = ""
bhstr = ""
rtstr = ""
timebintstr = "b"
tlimstr = "bbc"
partstr = "qP3d3f3fff3ff3f9f3f2f6f2fff3fff3ffff9f3ffffff3f{0}{1}{2}{3}{4}{5}{6}".format(
    chemistrystr, coolingstr, feedbackstr, bhstr, rtstr, timebintstr, tlimstr
)
if with_debug:
    partstr += "{0}{0}".format(integertimetstr)
print(partstr)
partstr = teststr
partstr = pad_bytes(partstr, swift_align)


def decode_str(string):
    return string[: string.find(b"\0")].decode("UTF-8")


def skip_block(file):
    block = file.read(struct.calcsize(headerstr))
    size, name = struct.unpack(headerstr, block)
    file.seek(size, 1)
    return decode_str(name), size


def read_block(file, blockstr, nblock=1):
    block = file.read(struct.calcsize(headerstr))
    size, name = struct.unpack(headerstr, block)
    blocksize = struct.calcsize(blockstr)
    if size != blocksize * nblock:
        print(
            "Size mismath {0} {1} {2} {3}!".format(
                size, blocksize, size / blocksize, nblock
            )
        )
        exit(1)
    data = []
    for iblock in range(nblock):
        block = file.read(blocksize)
        if iblock < 10:
            data.append(struct.unpack(blockstr, block))
    return decode_str(name), data


file = open("swift_000000.rst", "rb")

print(skip_block(file))
print(skip_block(file))
print(skip_block(file))
spacename, spacedata = read_block(file, spacestr)
print(spacename, spacedata)
npart = spacedata[0][spaceelements["nr_parts"]]
for i in range(19):
    print(skip_block(file))
name, data = read_block(file, partstr, npart)
print(name, data)
Particle = collections.namedtuple("Particle", varnames)
Particle._make(data[-1])
print(Particle.__dict__)
