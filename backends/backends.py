
from .create_session import create_session, close_session
#from .init_info import get_init_info

def setup_backends(app):
    app.on_startup.append(create_session)
    app.on_cleanup.append(close_session)

    #app.on_startup.append(get_init_info)

