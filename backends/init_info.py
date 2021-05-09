import os


async def get_init_info(app):
    ids = [int(i) for i in os.listdir(app['config']['inventory']['dir'])]
    app['N'] = max(ids) if len(ids) > 0 else 0


