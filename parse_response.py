import socket
import struct
import time
def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc
def parse_frame(data):
    if len(data) < 7:
        return None, None
    if data[0] != 0xAA or data[1] != 0x55:
        return None, None
    cmd = data[2]
    length = data[3]
    if len(data) < 4 + length + 2:
        return None, None
    recv_crc = struct.unpack('<H', data[4+length:4+length+2])[0]
    calc_crc = crc16(data[2:4+length])
    if recv_crc != calc_crc:
        print(f"CRC error: recv={recv_crc:04X}, calc={calc_crc:04X}")
        return None, None
    return cmd, data[4:4+length]
s = socket.socket()
s.connect(('localhost', 4444))
s.settimeout(1)
# 发送查询指令
s.send(b'\xAA\x55\x03\x00\x00\x00')
time.sleep(0.2)
try:
    data = s.recv(256)
    cmd, payload = parse_frame(data)
    if cmd == 0x81:
        joints = struct.unpack('<6f', payload)
        print("关节角度:", [round(j, 3) for j in joints])
    else:
        print("未收到有效响应")
except Exception as e:
    print("异常:", e)
s.close()
