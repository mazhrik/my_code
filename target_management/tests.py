from django.test import TestCase, Client

from .ess_controller import EssApiController
from .models import (SocialTarget,
                     GenericTarget)
from account_management.models import User

# Create your tests here.
IP = 'http://localhost'
ess_object = EssApiController()


# targets local test
#
# class TargetTest(TestCase):
#     def test_index(self):
#         c = Client()
#         c.login(username='myuser', password='mypassword')
#         idx_response = c.get("{0}/admin/".format(IP))
#         self.assertEqual(idx_response.status_code, 200)
#         create_response_social = c.get(
#             "{0}/admin/target_management/socialtarget/add/".format(IP))
#         self.assertEqual(create_response_social.status_code, 200)
#         create_response_generic = c.get(
#             "{0}/admin/target_management/generictarget/add/".format(IP))
#         self.assertEqual(create_response_generic.status_code, 200)
#
#     def test_model_creation(self):
#         user_test = User.objects.get(username='myuser')
#         # Test Model For Social target
#         social_target = SocialTarget.objects.create(
#             user=user_test,
#             target_url='http://aasdad423.com',
#             is_enabled=True,
#             expire_on='2020-11-27 09:09:19.000000',
#             created_on='2020-11-27 07:09:19.000000',
#             periodic_interval=20,
#             need_screenshot=True,
#             user_names='waleed',
#             generic_relation='onetoone',
#             target_type='tw',
#             target_sub_type='comp',
#             max_posts='12',
#             apply_ai=True,
#             target_status=True)
#
#         # Test Model For Generic target
#         generic_target = GenericTarget.objects.create(
#             user=user_test,
#             target_url='http://aasdad423.com',
#             is_enabled=True,
#             created_on='2020-11-27 07:09:19.000000',
#             expire_on='2020-11-27 09:09:19.000000',
#             periodic_interval=20,
#             need_screenshot=True,
#             title='this is title',
#             url='abcd.com',
#             ip='192.168.10.10',
#             domain='com',
#             pictures=True,
#             videos=True,
#             target_sub_type='comp',
#             headings=True,
#             paragraphs=True,
#             links=True,
#             target_type='tw',
#             target_status=True)
#
#         # Checking the saved data
#         self.assertEqual(social_target.user_names, "waleed")
#         self.assertEqual(social_target.max_posts, "12")
#         self.assertEqual(social_target.expire_on, '2020-11-27 09:09:19.000000')
#         self.assertEqual(generic_target.title, "this is title")
#         self.assertEqual(generic_target.ip, "192.168.10.10")
#         self.assertEqual(generic_target.expire_on,
#                          '2020-11-27 09:09:19.000000')
#
#     @classmethod
#     def setUpTestData(cls):
#         # store the password to login later
#
#         # Test User create for testing
#         password = 'mypassword'
#         my_admin = User.objects.create_superuser(
#             'myuser', 'myemail@test.com', password)
#         c = Client()
#         # You'll need to log him
#         # in before you can send requests through the client
#         c.login(username=my_admin.username,
#                 password=password)
#         user_test = User.objects.get(username='myuser')
#         SocialTarget.objects.create(user=user_test,
#                                     target_url='http://a.com',
#                                     is_enabled=True,
#                                     created_on='2020-11-27 07:09:19.000000',
#                                     expire_on='2020-11-27 09:09:19.000000',
#                                     periodic_interval=20,
#                                     need_screenshot=True,
#                                     user_names='waleed',
#                                     generic_relation='onetoone',
#                                     target_type='tw',
#                                     target_sub_type='comp',
#                                     max_posts='12',
#                                     apply_ai=True,
#                                     target_status=True)
#
#         GenericTarget.objects.create(
#             user=user_test,
#             target_url='http://aa.com',
#             is_enabled=True,
#             created_on='2020-11-27 07:09:19.000000',
#             expire_on='2020-11-27 09:09:19.000000',
#             periodic_interval=20,
#             need_screenshot=True,
#             title='this is title',
#             url='abcd.com',
#             ip='192.168.10.10',
#             domain='aasdasd',
#             pictures=True,
#             videos=True,
#             target_sub_type='comp',
#             headings=True,
#             paragraphs=True,
#             links=True,
#             target_type='tw',
#             target_status=True)
#
#     def test_model_get(self):
#         social_target = SocialTarget.objects.get(id=1)
#         self.assertEqual(social_target.id, 1)
#         self.assertIsInstance(social_target, SocialTarget)
#         generic_target = GenericTarget.objects.get(id=1)
#         self.assertEqual(generic_target.id, 1)
#         self.assertIsInstance(generic_target, GenericTarget)
#
#     def test_model_edit(self):
#         social_target_update = SocialTarget.objects.filter(id=1).update(
#             user_names='waleedkhan',
#             target_url='abc.com',
#             periodic_interval=23)
#         print(social_target_update)
#         edited_social = SocialTarget.objects.first()
#         self.assertEqual(edited_social.user_names, "waleedkhan")
#         self.assertEqual(edited_social.target_url, "abc.com")
#         self.assertEqual(edited_social.periodic_interval, 23)
#
#         generic_target_update = GenericTarget.objects.filter(id=1).update(
#             title='changedtitle',
#             paragraphs=False, ip='192.168.10.8')
#         print(generic_target_update)
#         edited_generic_target = GenericTarget.objects.first()
#         self.assertEqual(edited_generic_target.title, "changedtitle")
#         self.assertEqual(edited_generic_target.paragraphs, False)
#         self.assertEqual(edited_generic_target.ip, '192.168.10.8')
#
#     def test_model_delete(self):
#         num_deleted_social = SocialTarget.objects.get(id=1).delete()[0]
#         self.assertEqual(num_deleted_social, 1)
#         num_deleted_generic = GenericTarget.objects.get(id=1).delete()[0]
#         self.assertEqual(num_deleted_generic, 1)

# tests for api 192.168.18.19(ess_controller

class TestEssController(TestCase):
    def setUp(self):
        self.client = Client()
        # ess_object.add_sm_account(username='ameerhamza', password='test123', status=1, email='hamza@gmail.com',
        #                           userid='ameer.hamza')

    def test_details(self):
        response = self.client.get('getall_sm_account/')
        print(response)
        self.assertEqual(response.status_code, 200)
