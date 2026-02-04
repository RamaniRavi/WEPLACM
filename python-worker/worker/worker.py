import asyncio
import logging
import sys
from pyzeebe import ZeebeWorker, ZeebeClient, create_insecure_channel

from worker import (send_job_information, send_missing_info_WBIG)

send_job_information

async def main():
    # create connection
    channel_WBIG = create_insecure_channel(grpc_address="141.26.156.185:26500")
    channel_WPLACM = create_insecure_channel(grpc_address="141.26.156.184:26500")

    worker = ZeebeWorker(channel_WPLACM)
    client_WBIG = ZeebeClient(channel_WBIG)

    send_job_information.register(worker)
    send_missing_info_WBIG.register(worker)

    await worker.work()


if __name__ == '__main__':
    asyncio.run(main())
