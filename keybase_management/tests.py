# from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from .models import Keybase
from target_management.models import KeybaseTarget
from account_management.models import User


# Create your tests here.


class KeybaseTest(TestCase):
    def test_index(self):
        c = Client()
        c.login(username='myuser', password='mypassword')
        idx_response = c.get("http://127.0.0.1:8000/admin/")
        self.assertEqual(idx_response.status_code, 200)
        create_response = \
            c.get("http://127.0.0.1:8000/admin/"
                  "target_management/socialtarget/add/")
        self.assertEqual(create_response.status_code, 200)

    def test_model_creation(self):
        keybase = Keybase.objects.get(id=1)
        user_test = User.objects.get(username='myuser')
        # Test Model For Social target
        keybase_unit = Keybase.objects.create(
            title='test keybase',
            description='this is the desscription',
            keywords='{keyword1,keyword2}',
            mentions='{mention1,mention2}',
            is_expired=False, is_enabled=False,
            created_on='2020-11-27 07:09:19.000000',
            expire_on='2020-11-27 09:09:19.000000',
            updated_on='2020-11-27 08:09:19.000000',
            phrases='{this,are,phrases}',
            hashtags='{hashtag1,hashtag2}')

        # Test Model For Generic target
        keybase_target = KeybaseTarget.objects.create(
            user=user_test, keybase=keybase,
            keybase_title='this is test keybase',
            is_enabled=True, is_expired=False,
            generic_relation='general relation',
            created_on='2020-11-27 07:09:19.000000', site='social',
            expire_on='2020-11-27 09:09:19.000000', periodic_interval=20,
            target_url='example.com', need_screenshot=True,
            target_sub_type='comp',
            target_type='tw', target_status=True)

        # Checking the saved data
        self.assertEqual(keybase_unit.title, "test keybase")
        self.assertEqual(keybase_unit.keywords, "{keyword1,keyword2}")
        self.assertEqual(keybase_unit.created_on, '2020-11-27 07:09:19.000000')
        self.assertEqual(keybase_target.keybase_title, "this is test keybase")
        self.assertEqual(keybase_target.created_on,
                         '2020-11-27 07:09:19.000000')

    @classmethod
    def setUpTestData(cls):
        # store the password to login later

        # Test User create for testing
        password = 'mypassword'
        my_admin = User.objects.create_superuser('myuser',
                                                 'myemail@test.com', password)
        c = Client()
        # You'll need to log him in before
        # you can send requests through the client
        c.login(username=my_admin.username, password=password)
        user_test = User.objects.get(username='myuser')

        # Test Model For Generic target
        keybase = Keybase.objects.get(id=1)
        KeybaseTarget.objects.create(user=user_test, keybase=keybase,
                                     keybase_title='this is test keybase',
                                     is_enabled=True,
                                     is_expired=False,
                                     generic_relation='general relation',
                                     created_on='2020-11-27 07:09:19.000000',
                                     site='social',
                                     expire_on='2020-11-27 09:09:19.000000',
                                     periodic_interval=20,
                                     target_url='example1.com',
                                     need_screenshot=True,
                                     target_sub_type='comp',
                                     target_type='kb',
                                     target_status=True)

    def test_model_get(self):
        Keybase_unit = Keybase.objects.get(id=1)
        self.assertEqual(Keybase_unit.id, 1)
        self.assertIsInstance(Keybase_unit, Keybase)
        keybase_target = KeybaseTarget.objects.get(id=1)
        self.assertEqual(keybase_target.id, 1)
        self.assertIsInstance(keybase_target, KeybaseTarget)

    def test_model_edit(self):
        social_target_update = Keybase.objects.filter(id=1).update(
            title='keybase updated',
            keywords='{key1,key2}')
        print(social_target_update)
        edited_keybase_unit = Keybase.objects.first()
        self.assertEqual(edited_keybase_unit.title, "keybase updated")
        self.assertEqual(edited_keybase_unit.keywords, ['key1', 'key2'])

        keybase_target_update = KeybaseTarget.objects.filter(id=1).update(
            keybase_title='changedtitle',
            target_type='tw',
            site='news')
        print(keybase_target_update)
        edited_generic_target = KeybaseTarget.objects.first()
        self.assertEqual(edited_generic_target.keybase_title, "changedtitle")
        self.assertEqual(edited_generic_target.target_type, 'tw')
        self.assertEqual(edited_generic_target.site, 'news')

    def test_model_delete(self):
        num_deleted_generic = KeybaseTarget.objects.get(id=1).delete()[0]
        self.assertEqual(num_deleted_generic, 1)
        num_deleted_social = Keybase.objects.get(id=1).delete()[0]
        self.assertEqual(num_deleted_social, 1)
