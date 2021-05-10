from aiohttp import web
from functions.handler import create_user, add_voice, add_password, check, info, delete_user


def setup_routes(app):
    app.router.add_route('POST',
                         '/create_user',
                         create_user,
                         name='create_user')

    app.router.add_route('POST',
                         r'/delete_user/{id:\d+}',
                         delete_user,
                         name='delete_user')

    app.router.add_route('POST',
                         r'/add_voice/{id:\d+}',
                         add_voice,
                         name='add_voice')

    app.router.add_route('POST',
                         r'/add_password/{id:\d+}',
                         add_password,
                         name='add_password')

    app.router.add_route('POST',
                         r'/check/{id:\d+}',
                         check,
                         name='check')



    app.router.add_route('GET',
                         '/info',
                         info,
                         name='info')
