import asyncio
import signal
import sys

from rabbitmq_receiver_manager import RabbitMqReceiverManager

# Signal handler to gracefully shut down the consumer
async def shutdown(receiver, loop):
    """Gracefully shutdown the RabbitMQ connections"""
    print("Shutting down...")
    await receiver.close()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
                
    receiver = RabbitMqReceiverManager()
    
    await receiver.connect()
    
    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, 
            lambda: asyncio.create_task(shutdown(receiver, loop))
        )

    try:
        print("Starting message consumer...")
        await receiver.receive_message()
    except Exception as e:
        print(f"Error in consumer: {e}")
        await receiver.close()
        sys.exit(1)
        
if __name__ == "__main__":
    asyncio.run(main())