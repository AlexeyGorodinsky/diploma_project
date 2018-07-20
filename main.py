import json
import sys
import requests
from urllib.parse import urlencode


TOKEN = '3737236951798dcd10ab6624f775f640772b18f8aa71bc7deac7b39438172d73a929ade062ca899244958'
APP_ID = 6638070
API_VERSION = '5.80'
AUTH_URL = 'https://oauth.vk.com/authorize'
auth_params = {
    'client_id': APP_ID,
    'display': 'page',
    'scope': 'friends, users, groups ',
    'response_type': 'token',
    'v': API_VERSION
}

response = requests.get('?'.join((AUTH_URL, urlencode(auth_params))))
print('?'.join((AUTH_URL, urlencode(auth_params))))

class VkUser:
    def __init__(self):
        self.user_name = ''
        self.id = -1
        self.friends = list()
        self.communities = list()
        self.friends_communities = set()
        self.unique_groups = list()

    def get_id_by_user_name(self):
        self.id = requests.get('https://api.vk.com/method/users.get', params={
            'v': API_VERSION,
            'access_token': TOKEN,
            'user_ids': self.user_name
        }).json()['response'][0]['id']


    def get_communities(self, users):
        communities = []

        for i, user in enumerate(users):
            try:
                communities.extend(requests.get('https://api.vk.com/method/groups.get', params={
                    'v': API_VERSION,
                    'user_id': user,
                    'access_token': TOKEN
                }).json()['response']['items'])

            except:
                continue

        return communities

    def communities_info(self, communities):
        if not communities:
            return []

        communities_str = ''

        for i, community in enumerate(communities):
            communities_str += str(community) + ','
            communities_str = communities_str[:len(communities_str) - 1]

            response = requests.get('https://api.vk.com/method/groups.getById', params={
                'group_ids': communities_str,
                'v': API_VERSION,
                'access_token': TOKEN,
                'fields': 'members_count'
            })

        communities_info = response.json()['response']
        communities = list()
        temp_group = dict()
        for group in communities_info:
            temp_group['name'] = group['name']
            temp_group['id'] = group['id']
            temp_group['members_count'] = group['members_count']
            temp_group['screen_name'] = group['screen_name']

            communities.append(temp_group)

        return communities


    def unique_communities(self):
        for i, group in enumerate(self.communities):
            if group not in self.friends_communities:
                self.unique_groups.append(group)
        self.unique_groups = self.communities_info(self.unique_groups)

    def input_id(self):
        self.user_name = input('Введите id или имя пользователя: ')
        if not str(self.user_name).isdigit():
            self.get_id_by_user_name()

    def user_communities(self):
        print('Поиск сообществ пользователя', file=sys.stderr)
        self.communities = self.get_communities([self.id])
        print('ID сообществ пользователя:{}'.format(self.communities))

    def get_friends(self):
        print('Получение ID друзей пользователя', file=sys.stderr)
        self.friends = requests.get('https://api.vk.com/method/friends.get', params={
            'v': API_VERSION,
            'user_id': self.id,
            'access_token': TOKEN
        }).json()['response']['items']
        print('ID друзей пользователя:{}'.format(self.friends))

    def get_friends_communities(self):
        print('Получение сообществ друзей пользователя', file=sys.stderr)
        self.friends_communities = self.get_communities(self.friends)
        print('ID сообществ друзей пользователя: \n {}'.format(self.friends_communities))


    def get_unique_groups(self):
        self.input_id()
        self.user_communities()

        self.get_friends()
        self.get_friends_communities()

        print('Анализ сообществ пользователя и поиск уникальных, получение информации о сообществах', file=sys.stderr)
        self.unique_communities()
        print('Уникальные группы пользователя', self.unique_communities())


def unique_communities_json(user):
    if user.unique_groups:
        with open('result_{}.json' .format(user.user_name), 'w') as file:
            json.dump(user.unique_groups, file, indent=4, ensure_ascii=False)
    else:
        print('Уникальных сообществ не обнаружено')


user = VkUser()
user.get_unique_groups()
unique_communities_json(user)
