import struct
import re
import collections

default_align = 8
swift_align = 32


def pad_bytes(bytes, align=default_align):
    while struct.calcsize(bytes) % align:
        bytes += "x"
    return bytes


headerstr = "N21s"
headerstr = pad_bytes(headerstr)


def decode_str(string):
    return string[: string.find(b"\0")].decode("UTF-8")


def read_next_header(input_file):
    block = input_file.read(struct.calcsize(headerstr))
    if len(block) == 0:
        return None, None
    size, name = struct.unpack(headerstr, block)
    return decode_str(name), size


def write_header(output_file, header):
    block = struct.pack(headerstr, *header)
    output_file.write(block)


input_file = open("FLAM400/restart/swift_000000.rst", "rb")
# output_file = open("swift_copy.rst", "wb")
name, size = read_next_header(input_file)
while name:
    print(name, size)
    print(input_file.tell())
    #  block = input_file.read(size)
    input_file.seek(size, 1)
    #  write_header(output_file, (size, name.encode("UTF-8")))
    #  output_file.write(block)
    name, size = read_next_header(input_file)
