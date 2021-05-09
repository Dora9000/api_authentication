
from aiohttp import web
import argparse
import asyncio
import os
import signal
import traceback

from backends.backends import setup_backends
from logger import setup_logger
from routes import setup_routes
from settings import CONFIG_PATH, get_config, get_secure_config, test_config


def setup_config(app, config_path=None):
    try:
        if config_path is None:
            app['config'] = get_config(CONFIG_PATH)
            test_config(app['config'])
        else:
            app['config'] = get_config(config_path)
            test_config(app['config'])
    except Exception as e:
        app.logger.exception("config is broken.")
        return 1
    setup_logger(app)
    secure_config = get_secure_config(app['config'])
    app.logger.info(f"config: {secure_config}")
    return 0


def setup_app(config_path=None):
    #app_middlewares = middlewares()
    app = web.Application()
    status = setup_config(app, config_path)
    if status == 1:
        app.logger.error("Cant start app")
        exit(1)
    setup_backends(app)
    setup_routes(app)
    return app


@asyncio.coroutine
async def reload_config(app, config_path=None):
    app.logger.info(f"handling SIGHUP - reload_config and logger")
    secure_config = get_secure_config(app['config'])
    status = setup_config(app, config_path)
    if status == 1:
        app['config'] = secure_config
        app.logger.info(f"config was not reloaded")
    else:
        app.logger.info(f"config was reloaded")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--path')
    PARSER.add_argument('--port')
    PARSER.add_argument('--config')
    ARGS = PARSER.parse_args()

    OLD_UMASK = os.umask(0o022)
    os.umask(0)

    try:
        loop = asyncio.get_event_loop()
        app = setup_app(config_path=ARGS.config)
        #loop.add_signal_handler(signal.SIGHUP, lambda: asyncio.create_task(
        #    reload_config(app=app, config_path=ARGS.config)))
        web.run_app(app=app,
                    path=ARGS.path,
                    port=ARGS.port)
    except:
        print(traceback.format_exc())
    finally:
        os.umask(OLD_UMASK)
