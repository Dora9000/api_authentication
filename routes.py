from aiohttp import web
from functions.handler import create_user, add_voice, add_password, check, info, delete_user


def setup_routes(app):
    app.router.add_route('POST',
                         '/create_user',
                         create_user,
                         name='create_user')

    app.router.add_route('GET',
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
"""
    app.router.add_route('GET',
                         r'/notes/{id:\d+}',
                         notes_get_id,
                         name='notes_get_id')

    app.router.add_route('DELETE',
                         r'/notes/{id:\d+}',
                         notes_delete,
                         name='notes_delete')

    app.router.add_route('PUT',
                         r'/notes/{id:\d+}',
                         notes_put_id,
                         name='notes_put_id')
"""