from aiohttp import web
import json
import os


async def recognize_voice(app, id, file):
    return True
    pass


async def recognize_speech(app, id, file):
    return True
    pass


async def train_GMM(app, id):
    pass


async def download_file(request, path):
    try:
        with open(path, 'wb') as fd:
            while True:
                chunk = await request.content.read(10)
                if not chunk:
                    break
                fd.write(chunk)
    except Exception as e:
        print('download_file - ', e)
        return False
    return True


async def get_static(file):
    file_path = os.path.join(os.getcwd(), 'static', file)
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as static_file:
            static_content = static_file.read()
        return web.Response(body=static_content, status=200, content_type='text/html')
    else:
        raise web.HTTPNotFound()


async def create_user(request):
    id = request.app['N'] + 1
    request.app['N'] = id
    if not os.path.exists(request.app['config']['inventory']['dir'] + '/' + str(id)):
        os.makedirs(request.app['config']['inventory']['dir'] + '/' + str(id))
    else:
        return web.Response(status=400,
                            text=json.dumps({'text': 'cant create user {0}'.format(id)}),
                            content_type="application/json")
    return web.Response(status=200,
                        text=json.dumps({'text': 'ok', 'id': id}),
                        content_type="application/json")


async def add_voice(request):
    id = request.match_info['id']
    if not os.path.exists(request.app['config']['inventory']['dir'] + '/' + str(id)):
        return web.Response(status=400,
                            text=json.dumps({'text': 'user do not exist'}),
                            content_type="application/json")
    filename = request.app['config']['inputData']['dinamicDir'] + '/{0}.wav'.format(id)
    if await download_file(request, filename):
        old_filename = request.app['config']['inventory']['dir'] + '/' + str(id) + \
                       '/' + request.app['config']['inventory']['voiceDirName']
        await delete_path(old_filename)
        os.mkdir(old_filename)
        os.replace(filename, old_filename + '/1.wav')
    else:
        return web.Response(status=400,
                            text=json.dumps({'text': 'cant download'}),
                            content_type="application/json")
    # train GMM
    return web.Response(status=200,
                        text=json.dumps({'text': 'add_voice'}),
                        content_type="application/json")


async def add_password(request):
    id = request.match_info['id']
    if not os.path.exists(request.app['config']['inventory']['dir'] + '/' + str(id)):
        return web.Response(status=400,
                            text=json.dumps({'text': 'user do not exist'}),
                            content_type="application/json")
    data = request.query.get('password')
    if data and len(data) > 0:
        old_filename = request.app['config']['inventory']['dir'] + '/' + str(id) + \
                   '/' + request.app['config']['inventory']['pswdDirName']
        await delete_path(old_filename)
        os.mkdir(old_filename)
        with open(old_filename + '/1.txt', 'w+') as f:
            f.write(data)
    else:
        return web.Response(status=400,
                            text=json.dumps({'text': 'wrong params'}),
                            content_type="application/json")
    return web.Response(status=200,
                        text=json.dumps({'text': 'add_password'}),
                        content_type="application/json")


async def check(request):
    id = request.match_info['id']
    if not os.path.exists(request.app['config']['inventory']['dir'] + '/' + str(id)):
        return web.Response(status=401, text=json.dumps({'text': 'not allowed'}), content_type="application/json")

    filename = request.app['config']['inputData']['dinamicDir'] + '/check_{0}.wav'.format(id)
    if await download_file(request, filename):
        flag1 = await recognize_voice(request.app,id, filename)
        flag2 = await recognize_speech(request.app, id, filename)
        await delete_path(filename)
        if flag1 and flag2:
            web.Response(text=json.dumps({'text': 'ok'}), content_type="application/json")
        else:
            web.Response(status=401, text=json.dumps({'text': 'not allowed'}), content_type="application/json")
    return web.Response(text=json.dumps({'text': 'check'}), content_type="application/json")


async def delete_path(path):
    try:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)
    except Exception as e:
        print('delete_path - ', e)
        try:
            os.remove(path)
        except Exception as er:
            print('delete_path - ', e)
        return False
    return True


async def delete_user(request):
    id = request.match_info['id']
    path = request.app['config']['inventory']['dir'] + '/' + str(id)
    if not await delete_path(path):
        return web.Response(status=400,
                            text=json.dumps({'text': 'user does not exist'}),
                            content_type="application/json")
    else:
        print('user {0} deleted'.format(id))
        return web.Response(status=200,
                        text=json.dumps({'text': 'ok'}),
                        content_type="application/json")


async def get_users(app):
    users = os.listdir(app['config']['inventory']['dir'])
    answer = []
    for i in users:
        voice = pswd = 'no'
        factors = os.listdir(app['config']['inventory']['dir'] + '/' + str(i))
        if app['config']['inventory']['voiceDirName'] in factors:
            voice = 'yes'
        if app['config']['inventory']['pswdDirName'] in factors:
            pswd = 'yes'
        answer.append((i, voice, pswd, 'yes')) # id_, voice, pswd, active)
    return answer


async def info(request):
    print(request.app['N'])
    users = await get_users(request.app)
    data = []
    for (id_, voice, pswd, active) in users:
        data.append({'id': id_,
                     'voice_exist': voice,
                     'password_exist': pswd,
                     'active': active})
    return web.Response(status=200,
                        text=json.dumps(data, ensure_ascii=False),#.encode('utf8'),
                        content_type="application/json")


async def info_html(request):
    users = await get_users()
    data = ''
    users = ['<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'.format(id_, voice, pswd, active) for
                   (id_, voice, pswd, active) in users]
    for i in users:
        data += i
    print(data)
    content = '''<!DOCTYPE HTML><html><head><meta charset="utf-8"><title>Пользователи в базе</title></head><body><table border="1">
   <caption>Пользователи в базе</caption><tr><th>Идентификатор</th><th>Образец голоса</th><th>Наличие пароля</th><th>Активен</th>
   </tr>''' + data + '''</table></body></html>'''
    return web.Response(body=content, status=200, content_type='text/html')
    #return await get_static('w1.html')


"""
async def get_data_from_request(request):
    try:
        data = await request.text()
        data = json.loads(data)
    except Exception:
        data = await request.post()
    if data.get('content') is None and data.get('title') is None:
        return None
    return data


async def get_id(app):
    app['id'] += 1
    return app['id']


async def set_data_db(app, id, key, val):
    redis_server = app['redis']
    if val is not None:
        await redis_server.hset(id, key, val)


async def get_data_db(app, id, key):
    redis_server = app['redis']
    answer = await redis_server.hget(id, key)
    if answer is None:
        print(answer)
    return answer


async def get_data(app, id=None):
    redis_server = app['redis']
    answer = []
    if id is None:
        ids = await redis_server.keys('*')
        for _id in ids:
            title = await redis_server.hget(_id, 'title')
            content = await redis_server.hget(_id, 'content')
            answer.append({'id': int(_id.decode('ascii')),  # ("utf-8")
                           'title': content.decode('ascii')[:min(app['config']['N'], len(
                               content.decode('ascii')))] if title is None else title.decode('ascii'),
                           'content': content.decode('ascii')})
        return answer
    else:
        title = await redis_server.hget(id, 'title')
        content = await redis_server.hget(id, 'content')
        if content is None and title is None:
            return None
        return {'id': int(id),
                'title': content.decode('ascii')[:min(max(app['config']['N'], 0), len(
                    content.decode('ascii')))] if title is None else title.decode('ascii'),
                'content': content.decode('ascii')}


async def notes_get(request):
    filter = request.query.get('query')
    answers = await get_data(request.app)
    if filter is None:
        return web.Response(text=json.dumps(answers), content_type="application/json")
    else:
        filtered_answer = []
        for answer in answers:
            if answer.get('title').find(filter) != -1 or answer.get('content').find(filter) != -1:
                filtered_answer.append(answer)
        return web.Response(text=json.dumps(filtered_answer), content_type="application/json")


async def notes_get_id(request):
    if request.match_info['id'] is None:
        return web.Response(status=404,
                            text=json.dumps({"message": "not found"}),
                            content_type="application/json")
    answers = await get_data(request.app, id=request.match_info['id'])
    if answers is None:
        return web.Response(status=404,
                            text=json.dumps({"message": "not found"}),
                            content_type="application/json")
    return web.Response(text=json.dumps(answers), content_type="application/json")


async def notes_post(request):
    data = await get_data_from_request(request)
    if data is None or data.get('content') is None:
        return web.Response(status=405,
                            text=json.dumps({"message": "wrong params"}),
                            content_type="application/json")

    new_id = await get_id(request.app)
    await set_data_db(app=request.app, id=new_id, key='title', val=data.get('title'))
    await set_data_db(app=request.app, id=new_id, key='content', val=data.get('content'))
    answer = {"id": int(new_id), "content": data.get('content')}
    if data.get('title') is not None:
        answer["title"] = data.get('title')
    return web.Response(text=json.dumps(answer), content_type="application/json")


async def notes_delete(request):
    if request.match_info['id'] is None:
        return web.Response(status=405,
                            text=json.dumps({"message": "wrong params"}),
                            content_type="application/json")
    try:
        s = await request.app['redis'].delete(request.match_info['id'])
        if s == 0:
            return web.Response(status=404,
                                text=json.dumps({"message": "not found"}),
                                content_type="application/json")
    except Exception as e:
        print(e)
        return web.Response(status=403)
    return web.Response(text=json.dumps({"message": "ok"}), content_type="application/json")


async def notes_put_id(request):
    new_id = request.match_info['id']
    if new_id is None:
        return web.Response(status=405,
                            text=json.dumps({"message": "wrong params"}),
                            content_type="application/json")
    answers = await get_data(request.app, id=new_id)
    if answers is None:
        return web.Response(status=404,
                            text=json.dumps({"message": "not found"}),
                            content_type="application/json")
    data = await get_data_from_request(request)
    if data is None:
        return web.Response(status=405,
                            text=json.dumps({"message": "wrong params"}),
                            content_type="application/json")

    await set_data_db(app=request.app, id=new_id, key='title', val=data.get('title'))
    await set_data_db(app=request.app, id=new_id, key='content', val=data.get('content'))
    answer = {"id": int(new_id)}
    if data.get('title') is not None:
        answer["title"] = data.get('title')
    if data.get('content') is not None:
        answer["content"] = data.get('content')
    return web.Response(text=json.dumps(answer), content_type="application/json")
"""