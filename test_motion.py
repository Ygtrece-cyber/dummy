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
# 连接
s = socket.socket()
s.connect(('localhost', 4444))
s.settimeout(1)
# 1. 发送关节运动指令
joints = [0.5, -0.3, 0.8, -0.2, 0.4, 0.1]
payload = struct.pack('<6f', *joints)
print("发送关节指令:", joints)
s.send(build_frame(0x01, payload))
# 等待确认
try:
    data = s.recv(256)
    cmd, payload = parse_frame(data)
    if cmd == 0x82:
        recv_joints = struct.unpack('<6f', payload)
        print("收到确认帧，关节角度:", [round(j, 3) for j in recv_joints])
    else:
        print("未收到确认帧，收到指令码:", cmd)
except Exception as e:
    print("异常:", e)
s.close()
