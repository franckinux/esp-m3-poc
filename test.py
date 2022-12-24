import asyncio
import serial_asyncio


def at(cmd: str, no_plus=False) -> bytes:
    prefix = b"AT" if no_plus else b"AT+"
    s = prefix + cmd.encode() + b"\r\n"
    return s


class EspM3:
    def __init__(
            self,
            url: str,
            baudrate: int,
            address: str,
            port: int,
            ap: str,
            password: str
    ):
        self.__url = url
        self.__baudrate = baudrate
        self.__address = address
        self.__port = port
        self.__ap = ap
        self.__password = password

        self.__reader = None
        self.__writer = None
        self.__wifi_connected = False
        self.__connected = False

    async def async_init(self):
        coro = serial_asyncio.open_serial_connection(
            url=self.__url, baudrate=self.__baudrate
        )
        self.__reader, self.__writer = await coro

    async def __print_received_data(self):
        while True:
            s = await self.__reader.readline()
            print(s.decode(errors="ignore"), flush=True)

    async def __read_response(self):
        try:
            while True:
                line = await self.__reader.readline()
                line = line.decode(errors="ignore").strip()
                print(line)
                if line == "OK":
                    break
        except asyncio.CancelledError:
            pass

    async def run(self):
        self.__writer.write(at("RST"))
        await self.__read_response()
        await asyncio.sleep(1)

        # self.__writer.write(at("E0", no_plus=True))
        # await self.__read_response()
        # await asyncio.sleep(1)

        self.__writer.write(at("CWAUTOCONN=0"))
        await self.__read_response()
        await asyncio.sleep(1)

        self.__writer.write(at("CWMODE=1"))
        await self.__read_response()
        await asyncio.sleep(1)

        self.__writer.write(at(f'CWJAP="{self.__ap}","{self.__password}"'))
        await self.__read_response()
        await asyncio.sleep(1)

        self.__writer.write(at("CIFSR"))
        await self.__read_response()
        await asyncio.sleep(1)

        self.__writer.write(at(f'CIPSTART="TCP","{self.__address}",{self.__port}'))
        await self.__read_response()
        await asyncio.sleep(1)

        self.__writer.write(at("CIPMODE=1"))
        await self.__read_response()
        await asyncio.sleep(1)

        self.__writer.write(at("CIPSEND"))
        await self.__read_response()
        await asyncio.sleep(1)

        task = asyncio.create_task(self.__print_received_data())

        for _ in range(5):
            self.__writer.write(b"bonjour\n\r")
            await asyncio.sleep(1)
        print("ending wifi passthrough mode")
        self.__writer.write(b"+++")
        await asyncio.sleep(2)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        self.__writer.write(at("CIPMODE=0"))
        await self.__read_response()
        await asyncio.sleep(2)

        self.__writer.write(at("CIPCLOSE"))
        await self.__read_response()
        await asyncio.sleep(2)

        self.__writer.write(at("CWQAP"))
        await self.__read_response()
        await asyncio.sleep(2)


class MyProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        infos = transport.get_extra_info("peername")
        print(f"connection from remote address {infos[0]}, port {infos[1]}")
        self.__transport = transport

    def data_received(self, data):
        print(data)
        self.__transport.write(b"hello\n\r")


async def server():
    loop = asyncio.get_running_loop()
    await loop.create_server(MyProtocol, "0.0.0.0", 8080)


async def main():
    asyncio.create_task(server())

    esp = EspM3(
        "/dev/ttyACM0",
        115200,
        "192.168.1.114",
        8080,
        "Livebox-79D0",
        "C3EA70F21E7867881736480366"
    )
    await esp.async_init()
    await esp.run()


if __name__ == "__main__":
    asyncio.run(main())
