from asyncio import create_task
import logging

log = logging.getLogger(__name__)

class Dispatcher:
    def __init__(self, parent):
        self.parent = parent

    def push(self, client, packet):
        op_code = packet.op_code

        log.debug("Recieved : [%s] [%s]", op_code, packet.to_string())

        try:
            coro = None

            for packet_handler in self.parent._packet_handlers:
                if packet_handler.op_code == op_code:
                    coro = packet_handler.callback
                    break
            
            if not coro:
                raise AttributeError

        except AttributeError:
            log.debug(f"Unhandled event in {self.parent} : {op_code}")

        else:
            self.parent._loop.create_task(self._run_event(coro, client, packet))
    
    async def _run_event(self, coro, *args):
        # try:
        await coro(self.parent, *args)
        
        # except Exception as e:
        #     print(f"Event method {coro.__name__} threw : {e}")