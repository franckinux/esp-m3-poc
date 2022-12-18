import serial
import sys
import time

def at(cmd: str, no_plus=False) -> str:
    prefix = b"AT" if no_plus else b"AT+"
    s =  prefix + cmd.encode() + b"\r\n"
    return s


with serial.Serial(port="/dev/ttyACM0", baudrate=115200, parity=serial.PARITY_NONE, timeout=10) as ser:
    try:
        # ser.write(at('', no_plus=True))
        # r = ser.read(256).decode(errors="ignore")
        # print(r)

        ser.write(at("RST"))
        r = ser.read(256).decode(errors="ignore")
        print(r)

        # ser.write(b"ATE0\r\n")
        # r = ser.read(256).decode(errors="ignore")
        # print(r)

        ser.write(at("CWMODE=3"))
        r = ser.read(256).decode(errors="ignore")
        print(r)

        ser.write(at("CWLAP"))
        r = ser.read(256).decode(errors="ignore")
        print(r)
    except KeyboardInterrupt:
        sys.exit()

    try:
        print("opening connection")
        ser.write(at('CWJAP="Livebox-79D0","C3EA70F21E7867881736480366"'))
        r = ser.read(256).decode(errors="ignore")
        print(r)

        ser.write(at("CIFSR"))
        r = ser.read(256).decode(errors="ignore")
        print(r)

        print("IP address ? ", end="")
        address = input().strip()
        print("port? ", end="")
        port = int(input())
        print()

        ser.write(at(f'CIPSTART="TCP","{address}",{port}'))
        r = ser.read(256).decode(errors="ignore")
        print(r)

        ser.write(at("CIPMOD=1"))
        r = ser.read(256).decode(errors="ignore")
        print(r)

        ser.write(at("CIPSEND"))
        r = ser.read(256).decode(errors="ignore")

        print("reception test")
        try:
            while True:
                r = ser.read(256).decode(errors="ignore")
                print(r)
        except KeyboardInterrupt:
            breakpoint()

        ser.write(at("CIPMOD=0"))
        r = ser.read(256).decode(errors="ignore")
        print(r)

    finally:
        print("closing connection")
        ser.write(at("CIPCLOSE"))
        r = ser.read(256).decode(errors="ignore")
        print(r)
