import chip64

code = [
    # 0xF0, 0x01, # r0 = input()
    0xF1, 0x01, # r1 = input()
    0x62, 0x00, # total = 0
    0x63, 0x00, # r3 = 0
#loop_top
    0x43, 0x40, # skip next if r3 == 64
    0x10, 0x18, # goto loop_end
    0x80, 0x16, # r0 >>= 1
    0x3F, 0x00, # skip next if carry == 0
    0x82, 0x14, # total += r1
    0x81, 0x1E, # r1 <<= 1
    0x73, 0x01, # r3 += 1
    0x10, 0X08, # goto loop_top
# loop_end
    # 0xD0, 0x01  # print(total)
]

if __name__ == "__main__":
    chip64.Chip64(code).execute()
