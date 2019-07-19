from loguru import logger


class Dispatcher:
    def __init__(self, parent):
        self.parent = parent

    # def push_event(self, *args):
    #     try:
    #         coro = None

    #         for packet_handler in self.parent._packet_handlers:
    #             if packet_handler.op_code == op_code:
    #                 coro = packet_handler.callback
    #                 break

    #         if not coro:
    #             raise AttributeError

    #     except AttributeError:
    #         ("Unhandled event in %s : %s",
    #                  self.parent.name, op_code.name)

    #     else:
    #         self.parent._loop.create_task(
    #             self._run_event(coro, client, packet))

    def push(self, client, packet):
        if client.__class__.__name__ == "socket":
            logger.packet(
                f"{packet.name} {client.getpeername()[0]} {packet.debug_string}", "in")
        else:
            logger.packet(
                f"{packet.name} {client.ip} {packet.debug_string}", "in")

        try:
            coro = None

            for packet_handler in self.parent._packet_handlers:
                if packet_handler.op_code == packet.op_code:
                    coro = packet_handler.callback
                    break

            if not coro:
                raise AttributeError

        except AttributeError:
            logger.warning(
                f"Unhandled event in {self.parent.name} : <w>{packet.name}</w>")

        else:
            self.parent._loop.create_task(
                self._run_event(coro, client, packet))

    async def _run_event(self, coro, *args):
        # try:
        await coro(self.parent, *args)

        # except Exception as e:
        #     log.warn("Event method %s threw : %s", coro.__name__, e)
