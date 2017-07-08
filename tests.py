#!/usr/bin/env python -W ignore
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import os

from app import app
from app.models import *
from install import populate_db

import unittest
import tempfile
import json


class AppTestCase(unittest.TestCase):
    token = None

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s \
            ' % app.config['DATABASE']
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            populate_db._run()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_user_admin_from_db(self):
        users = User.query.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'admin')
        self.assertTrue(users[0].verify_password('admin'))

    def test_get_auth(self):
        rv = self.app.post('/api/v1/auth', data=json.dumps({
            'username': 'admin',
            'password': 'admin'
        }), content_type='application/json')
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertIn('access_token', rj)
        self.__class__.token = rj['access_token']

    def test_get_lwp_users(self):
        rv = self.app.get(
            '/api/v1/lwp/users', headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(len(rj['data']), 1)
        self.assertEqual(rj['data'][0]['id'], 1)
        self.assertEqual(rj['data'][0]['type'], 'users')

    def test_get_lwp_users_1(self):
        rv = self.app.get(
            '/api/v1/lwp/users/1', headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rj['data']['id'], 1)
        self.assertTrue(rj['data']['attributes']['admin'])
        self.assertEqual(rj['data']['attributes']['username'], 'admin')
        self.assertEqual(rj['data']['attributes']['name'], 'John Doe')
        self.assertIsNone(rj['data']['attributes']['email'])
        self.assertEqual(rj['data']['type'], 'users')

    def test_put_lwp_users_1(self):
        rv = self.app.put(
            '/api/v1/lwp/users/1',
            data=json.dumps({
                "data": {
                    "attributes": {
                        "admin": False,
                        "email": "elie@deloumeau.fr",
                        "name": "Élie Deloumeau",
                        "password": "elie",
                    },
                    "type": "users"
                }
            }),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rj['data']['id'], 1)
        self.assertFalse(rj['data']['attributes']['admin'])
        self.assertEqual(rj['data']['attributes']['username'], 'admin')
        self.assertEqual(rj['data']['attributes']['name'], 'Élie Deloumeau')
        self.assertEqual(rj['data']['attributes'][
                         'email'], 'elie@deloumeau.fr')
        self.assertEqual(rj['data']['type'], 'users')

    def test_delete_lwp_users_1(self):
        rv = self.app.delete(
            '/api/v1/lwp/users/1',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        # Assert token error : Not enough segments
        self.assertEqual(rv.status_code, 422)
        self.assertEqual(rj['msg'], 'Not enough segments')

    def test_post_lwp_users(self):
        rv = self.app.post(
            '/api/v1/lwp/users',
            data=json.dumps({
                "data": {
                    "attributes": {
                        "admin": False,
                        "email": "test@test.test",
                        "name": "test",
                        "password": "test",
                        "username": "test"
                    },
                    "type": "users"
                }
            }),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 201)
        self.assertEqual(rj['data']['id'], 2)
        self.assertFalse(rj['data']['attributes']['admin'])
        self.assertEqual(rj['data']['attributes']['username'], 'test')
        self.assertEqual(rj['data']['attributes']['name'], 'test')
        self.assertEqual(rj['data']['attributes']['email'], 'test@test.test')
        self.assertEqual(rj['data']['type'], 'users')

    def test_get_lwp_me(self):
        rv = self.app.get(
            '/api/v1/lwp/me', headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rj['data']['id'], 1)
        self.assertTrue(rj['data']['attributes']['admin'])
        self.assertEqual(rj['data']['attributes']['username'], 'admin')
        self.assertEqual(rj['data']['attributes']['name'], 'John Doe')
        self.assertIsNone(rj['data']['attributes']['email'])
        self.assertEqual(rj['data']['type'], 'users')

    def test_put_lwp_me(self):
        rv = self.app.put(
            '/api/v1/lwp/me',
            data=json.dumps({
                "data": {
                    "attributes": {
                        "admin": False,
                        "email": "elie@deloumeau.fr",
                        "name": "Élie Deloumeau",
                        "password": "elie",
                    },
                    "type": "users"
                }
            }),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rj['data']['id'], 1)
        self.assertFalse(rj['data']['attributes']['admin'])
        self.assertEqual(rj['data']['attributes']['username'], 'admin')
        self.assertEqual(rj['data']['attributes']['name'], 'Élie Deloumeau')
        self.assertEqual(rj['data']['attributes'][
                         'email'], 'elie@deloumeau.fr')
        self.assertEqual(rj['data']['type'], 'users')

    def test_delete_me(self):
        rv = self.app.delete(
            '/api/v1/lwp/me',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        # Assert token error : Not enough segments
        self.assertEqual(rv.status_code, 422)
        self.assertEqual(rj['msg'], 'Not enough segments')

    def test_get_lwp_groups(self):
        rv = self.app.get(
            '/api/v1/lwp/groups', headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(len(rj['data']), 1)
        self.assertEqual(rj['data'][0]['id'], 1)
        self.assertEqual(rj['data'][0]['type'], 'groups')

    def test_get_lwp_groups_1(self):
        rv = self.app.get(
            '/api/v1/lwp/groups/1', headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rj['data']['id'], 1)
        self.assertEqual(rj['data']['attributes']['name'], 'admin')
        self.assertEqual(rj['data']['type'], 'groups')

    def test_put_lwp_groups_1(self):
        rv = self.app.put(
            '/api/v1/lwp/groups/1',
            data=json.dumps({
                "data": {
                    "attributes": {
                        "name": "admin-test",
                    },
                    "type": "groups"
                }
            }),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rj['data']['id'], 1)
        self.assertEqual(rj['data']['attributes']['name'], 'admin-test')
        self.assertEqual(rj['data']['type'], 'groups')

    def test_delete_lwp_groups_1(self):
        rv = self.app.delete(
            '/api/v1/lwp/groups/1',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

    def test_post_lwp_groups(self):
        rv = self.app.post(
            '/api/v1/lwp/groups',
            data=json.dumps({
                "data": {
                    "attributes": {
                        "name": "test"
                    },
                    "type": "groups"
                }
            }),
            content_type='application/json',
            headers={
                'Authorization': 'Bearer %s' % self.__class__.token
            })
        rj = json.loads(rv.get_data(as_text=True))

        self.assertEqual(rv.status_code, 201)
        self.assertEqual(rj['data']['id'], 2)
        self.assertEqual(rj['data']['attributes']['name'], 'test')
        self.assertEqual(rj['data']['type'], 'groups')


if __name__ == '__main__':
    unittest.main()
