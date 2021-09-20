from utils import log


class Dispatcher:
    def __init__(self, parent):
        self.parent = parent

    def push(self, client, packet):
        log.packet(f"{self.parent.name} {packet.name} {client.ip} {packet.to_string()}", "in")

        try:
            coro = None

            for packet_handler in self.parent._packet_handlers:
                if packet_handler.op_code == packet.op_code:
                    coro = packet_handler.callback
                    break

            if not coro:
                raise AttributeError

        except AttributeError:
            log.warning(
                f"{self.parent.name} Unhandled event in : <w>{packet.name}</w>")

        else:
            self.parent._loop.create_task(
                self._run_event(coro, client, packet))

    async def _run_event(self, coro, *args):
        await coro(self.parent, *args)
