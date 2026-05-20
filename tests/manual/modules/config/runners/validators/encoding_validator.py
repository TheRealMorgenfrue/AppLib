def compatible_bit_depth(segment: bool, bit_depth: str):
    print(segment, bit_depth)
    if segment and bit_depth.lower() == "16bit":
        raise ValueError("16bit input is not supported with segmentation")
