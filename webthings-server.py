import asyncio
import logging

from webthing import MultipleThings, WebThingServer

from kupcimat.generator import generate_webthings


def run_server():
    webthings = generate_webthings("webthings-mapping.yaml")
    loop = asyncio.get_event_loop()
    things = [thing for thing, _ in webthings]
    update_tasks = [loop.create_task(update_task()) for _, update_task in webthings]

    server = WebThingServer(things=MultipleThings(things, name="home"),
                            port=8888,
                            hostname="host.docker.internal")
    try:
        logging.info("starting the server")
        server.start()
    except KeyboardInterrupt:
        logging.info("stopping background tasks")
        for task in update_tasks:
            task.cancel()
        logging.info("stopping the server")
        server.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
