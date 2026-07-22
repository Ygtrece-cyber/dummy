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
    # 查找第一个 0xAA 0x55
    start = 0
    while start < len(data) - 1:
        if data[start] == 0xAA and data[start+1] == 0x55:
            break
        start += 1
    if start >= len(data) - 1:
        return None, None
    # 检查是否有足够长度
    if len(data) - start < 7:
        return None, None
    # 取帧
    frame = data[start:]
    cmd = frame[2]
    length = frame[3]
    if len(frame) < 4 + length + 2:
        return None, None
    recv_crc = struct.unpack('<H', frame[4+length:4+length+2])[0]
    calc_crc = crc16(frame[2:4+length])
    if recv_crc != calc_crc:
        print(f"CRC error: recv={recv_crc:04X}, calc={calc_crc:04X}")
        return None, None
    return cmd, frame[4:4+length]
def build_frame(cmd, payload=b''):
    frame = bytearray([0xAA, 0x55, cmd, len(payload)]) + payload
    crc = crc16(frame[2:])
    frame += struct.pack('<H', crc)
    return bytes(frame)
s = socket.socket()
s.connect(('localhost', 4444))
s.settimeout(2)
# 先接收可能存在的 telnet 协商数据（自动发送的响应帧可能已经到来）
# 我们发送查询指令
print("Sending query...")
s.send(build_frame(0x03))
# 接收数据
data = b''
while len(data) < 28:  # 最小响应帧长度
    try:
        chunk = s.recv(256)
        if not chunk:
            break
        data += chunk
    except socket.timeout:
        break
print(f"Received raw data length: {len(data)}")
if len(data) > 0:
    cmd, payload = parse_frame(data)
    if cmd == 0x81 and len(payload) == 24:
        joints = struct.unpack('<6f', payload)
        print("关节角度:", [round(j, 3) for j in joints])
    else:
        print(f"未解析到有效帧，cmd={cmd}")
        # 打印原始十六进制
        print("Hex:", data.hex())
else:
    print("No data received")
s.close()
