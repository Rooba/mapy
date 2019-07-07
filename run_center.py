import asyncio

from common.constants import SECRET_KEY
from server import CenterServer

loop = asyncio.get_event_loop()
CS = CenterServer(loop, security_key=SECRET_KEY)

try:
    loop.run_forever()
    
except KeyboardInterrupt:
    print(f"Shutting down {CS.name}")

finally:
    for task in asyncio.Task.all_tasks():
        task.cancel()

    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
