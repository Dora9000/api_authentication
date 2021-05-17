import json
import requests
import unittest
import random
import time

data_path = 'C:/Users/super/PycharmProjects/auth_api/data/test_data/1.wav'


class TestAPI(unittest.TestCase):

    def create_user(self):
        r = requests.post('http://localhost:8080/create_user')
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')
        return answer['id']

    def create_users(self):
        for id_ in range(100):
            r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
        users_list = []
        for i in range(100):
            users_list.append(self.create_user())
        for i in range(500):
            id_ = random.randint(max(users_list) + 1, max(users_list) + 501)
            if id_ in users_list:
                print(id_)
                continue
            r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
            self.assertEqual(r.status_code, 400)
            answer = json.loads(r.text)
            self.assertEqual(answer['text'], 'user does not exist')

        for id_ in users_list:
            r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
            self.assertEqual(r.status_code, 200)
            answer = json.loads(r.text)
            self.assertEqual(answer['text'], 'ok')

        for id_ in range(max(users_list) + 1):
            r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
            self.assertEqual(r.status_code, 400)
            answer = json.loads(r.text)
            self.assertEqual(answer['text'], 'user does not exist')

    def test_create_users(self):
        self.create_users()

    def test_add_delete_data(self):
        users_list = set()
        for j in range(3):
            id_ = self.create_user()
            users_list.add(id_)
            for _ in range(3):
                self.add_voice(id_)
            r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
            self.assertEqual(r.status_code, 200)
            answer = json.loads(r.text)
            self.assertEqual(answer['text'], 'ok')
        for id_ in users_list:
            r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
            self.assertEqual(r.status_code, 400)
            answer = json.loads(r.text)
            self.assertEqual(answer['text'], 'user does not exist')

    def test_add_data(self):
        # user one
        id_ = self.create_user()
        self.add_voice(id_)
        r = requests.post('http://localhost:8080/check/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')  # {'text': 'not allowed'} ['speech'] = 'not done'
        self.assertEqual(answer['speech'], 'not done')
        #self.assertEqual(answer.get('speech'), None)
        self.assertEqual(answer.get('voice'), None)

        self.add_speech(id_)
        r = requests.post('http://localhost:8080/check/{0}'.format(id_))
        answer = json.loads(r.text)
        print(answer)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(answer['text'], 'ok')
        self.assertEqual(answer.get('speech'), None)
        self.assertEqual(answer.get('voice'), None)

        r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')

        # user two
        id_ = self.create_user()
        self.add_speech(id_)
        r = requests.post('http://localhost:8080/check/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')  # {'text': 'not allowed'} ['speech'] = 'not done'
        #self.assertEqual(answer['voice'], 'not done')
        self.assertEqual(answer.get('speech'), None)
        self.assertEqual(answer.get('voice'), 'not done')

        self.add_voice(id_)
        r = requests.post('http://localhost:8080/check/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')
        self.assertEqual(answer.get('speech'), None)
        self.assertEqual(answer.get('voice'), None)

        r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')

        # user three
        id_ = self.create_user()
        r = requests.post('http://localhost:8080/check/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')  # {'text': 'not allowed'} ['speech'] = 'not done'
        self.assertEqual(answer['voice'], 'not done')
        self.assertEqual(answer['speech'], 'not done')

        self.add_speech(id_)
        self.add_voice(id_)
        r = requests.post('http://localhost:8080/check/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')
        self.assertEqual(answer.get('speech'), None)
        self.assertEqual(answer.get('voice'), None)

        r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')

    def test_info_valid(self):
        users_list = set()
        for i in range(100):
            users_list.add(self.create_user())
        users_list_voice = random.sample(users_list, 20)
        users_list_speech = random.sample(users_list, 20)
        for i in users_list_voice:
            self.add_voice(i)
        for i in users_list_speech:
            self.add_speech(i)

        users_list_voice = set(users_list_voice)
        users_list_speech = set(users_list_speech)

        r = requests.get('http://localhost:8080/info')
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        for one_answer in answer:
            id_ = int(one_answer['id'])
            voice = one_answer['voice_exist']
            pswd = one_answer['password_exist']
            active = one_answer['active']

            self.assertTrue(id_ in users_list)
            self.assertEqual(active, 'yes')
            if id_ in users_list_speech:
                self.assertEqual(pswd, 'yes')
            else:
                self.assertEqual(pswd, 'no')
            if id_ in users_list_voice:
                self.assertEqual(voice, 'yes')
            else:
                self.assertEqual(voice, 'no')

        for id_ in users_list:
            r = requests.post('http://localhost:8080/delete_user/{0}'.format(id_))
            self.assertEqual(r.status_code, 200)
            answer = json.loads(r.text)
            self.assertEqual(answer['text'], 'ok')

    def add_voice(self, id_):

        with open(data_path, 'rb') as f:
            data = f
            headers = {'content-type': 'audio/wav'}
            start = time.time()
            r = requests.post('http://localhost:8080/add_voice/{0}'.format(id_), data=data, headers=headers)
            print(time.time() - start)
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')

    def add_speech(self, id_):
        pswd = 'key phrase for auth api. user number is {0}'.format(id_)
        r = requests.post('http://localhost:8080/add_password/{0}'.format(id_),
                          data=json.dumps({'password': pswd}))
        self.assertEqual(r.status_code, 200)
        answer = json.loads(r.text)
        self.assertEqual(answer['text'], 'ok')


if __name__ == '__main__':
    unittest.main()
