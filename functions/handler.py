from aiohttp import web
import json
import os
from .speech_recognition import predict
from .voice_identification import create_gmm, predict_voice


async def recognize_voice(app, id_, file):
    print('recognize_voice - done')

    if not os.path.exists(app['config']['inventory']['dir'] + '/' + str(id_) +
                          '/' + app['config']['inventory']['voiceDirName']):
        return 2
    features_path = app['config']['inventory']['dir'] + '/' + str(id_) + \
                    '/' + app['config']['inventory']['voiceDirName'] + '/features'
    if not os.path.exists(features_path):
        os.makedirs(features_path)
    id2 = predict_voice(app, file, features_path)
    await delete_path(features_path)
    if id_ == id2:
        return 0
    return 1


async def recognize_speech(app, id_, file):
    print('recognize_speech - done')
    if not os.path.exists(app['config']['inventory']['dir'] + '/' + str(id_) +
                          '/' + app['config']['inventory']['pswdDirName']):
        return 2
    answer1 = answer2 = ''
    answer1 = predict(app, file)
    with open(app['config']['inventory']['dir'] + '/' + str(id_) +
              '/' + app['config']['inventory']['pswdDirName'] + '/1.txt', "r") as f:
        answer2 = f.read()
    print('recognize_speech -', answer1)
    if answer1 == answer2:
        return 0
    return 1


async def train_GMM(app, id_):
    create_gmm(app, app['config']['voiceSystem']['dir'], id_)
    print('train_GMM - done')
    return


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
    ids = [int(i) for i in os.listdir(request.app['config']['inventory']['dir'])]
    id = (max(ids) if len(ids) > 0 else 0) + 1
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

    await train_GMM(request.app, id)  # train GMM
    return web.Response(status=200,
                        text=json.dumps({'text': 'ok'}),
                        content_type="application/json")


async def get_data_from_request(request):
    try:
        data = await request.text()
        data = json.loads(data)
    except Exception:
        data = await request.post()
    if data.get('password') is None:
        data = data.get('content')
    else:
        data = data.get('password')
    return data


async def add_password(request):
    id = request.match_info['id']
    if not os.path.exists(request.app['config']['inventory']['dir'] + '/' + str(id)):
        return web.Response(status=400,
                            text=json.dumps({'text': 'user do not exist'}),
                            content_type="application/json")
    # data = request.query.get('password')
    data = await get_data_from_request(request)
    print('add_password - ', data)
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
                        text=json.dumps({'text': 'ok'}),
                        content_type="application/json")


async def check(request):
    id = request.match_info['id']
    if not os.path.exists(request.app['config']['inventory']['dir'] + '/' + str(id)):
        return web.Response(status=401, text=json.dumps({'text': 'not allowed'}), content_type="application/json")

    filename = request.app['config']['inputData']['dinamicDir'] + '/check_{0}.wav'.format(id)
    if await download_file(request, filename):
        flag1 = await recognize_voice(request.app, id, filename)
        flag2 = await recognize_speech(request.app, id, filename)

        await delete_path(filename)
        if flag1 == 0 or flag1 == 2 and flag2 == 0 or flag2 == 2:
            text = {'text': 'ok'}
            if flag1 == 2:
                text['voice'] = 'not done'
            if flag2 == 2:
                text['speech'] = 'not done'
            return web.Response(text=json.dumps(text), content_type="application/json")
        else:
            text = {'text': 'not allowed'}
            if request.app['config']['app']['test']:
                if flag1 == 1:
                    text['voice'] = 'not allowed'
                if flag2 == 1:
                    text['speech'] = 'not allowed'
            return web.Response(status=401, text=json.dumps(text), content_type="application/json")
    return web.Response(status=400, text=json.dumps({'text': 'cant download file'}), content_type="application/json")


async def delete_path(path):
    try:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)
            return True
    except Exception as e:
        # print('delete_path 1 - ', e)
        try:
            os.remove(path)
            return True
        except Exception as er:
            print('delete_path 2 - ', e)
            return False


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
        answer.append((i, voice, pswd, 'yes'))  # id_, voice, pswd, active)
    return answer


async def info(request):
    users = await get_users(request.app)
    data = []
    for (id_, voice, pswd, active) in users:
        data.append({'id': id_,
                     'voice_exist': voice,
                     'password_exist': pswd,
                     'active': active})
    return web.Response(status=200,
                        text=json.dumps(data, ensure_ascii=False),  # .encode('utf8'),
                        content_type="application/json")


async def info_html(request):
    users = await get_users(request.app)
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
    # return await get_static('w1.html')
