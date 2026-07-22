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
def build_frame(cmd, payload=b''):
    frame = bytearray([0xAA, 0x55, cmd, len(payload)]) + payload
    crc = crc16(frame[2:])
    frame += struct.pack('<H', crc)
    return bytes(frame)
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
        return None, None
    return cmd, data[4:4+length]
s = socket.socket()
s.connect(('localhost', 4444))
s.settimeout(2)
joints = [0.5, -0.3, 0.8, -0.2, 0.4, 0.1]
payload = struct.pack('<6f', *joints)
frame = build_frame(0x01, payload)
print("发送关节指令:", joints)
s.send(frame)
# 接收所有数据
data = s.recv(1024)
print("原始接收 (hex):", data.hex())
# 尝试解析帧
cmd, _ = parse_frame(data)
if cmd == 0x82:
    print("收到确认帧 (ACK) ✅")
elif cmd is not None:
    print(f"收到其他指令码: 0x{cmd:02X}")
else:
    print("未解析到有效帧")
s.close()
