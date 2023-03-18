from django.test import TestCase, Client
from .models import Individual, Group, Event
from account_management.models import User
from keybase_management.models import Keybase

# Create your tests here.
IP = 'http://localhost'


class PortfolioTest(TestCase):
    def test_index(self):
        c = Client()
        c.login(username='myuser', password='mypassword')
        idx_response = c.get("{0}/admin/".format(IP))
        self.assertEqual(idx_response.status_code, 200)

    def test_model_creation(self):
        # user_test = User.objects.get(username='myuser')
        # Test Model For Individuals

        user_test = User.objects.get(username="myuser")
        keybase = Keybase.objects.get(id=1)

        # Test Models For Individuals
        individual = Individual.objects.create(
            user=user_test, title='individuals_title',
            created_on='2020-11-27 07:09:19.000000',
            updated_on='2020-11-27 07:09:19.000000',
            expire_on='2020-11-27 09:09:19.000000',
            addresses="{dummy address1,dummy address2}",
            phone_numbers="{090078601,12345578911}",
            descriptions="{desc1,desc2}",
            date_of_birth='2020-11-27', gender='male',
            religion='islam', sect="abc", )

        individual.save()
        individual.keybase.add(keybase)
        # Test Models For Group
        group = Group.objects.create(
            user=user_test, title='group_title',
            created_on='2020-11-27 07:09:19.000000',
            updated_on='2020-11-27 07:09:19.000000',
            expire_on='2020-11-27 09:09:19.000000',
            addresses="{dummy address1,dummy address2}",
            phone_numbers="{090078601,12345578911}",
            descriptions="{desc1,desc2}",
            group_type="my_group", region='Islamabad',
            details="group_details")
        group.save()
        group.keybase.add(keybase)
        # Test Models For Event
        event = Event.objects.create(
            user=user_test, title='event_title',
            created_on='2020-11-27 07:09:19.000000',
            updated_on='2020-11-27 07:09:19.000000',
            expire_on='2020-11-27 09:09:19.000000',
            addresses="{dummy address1,dummy address2}",
            phone_numbers="{090078601,12345578911}",
            descriptions="{desc1,desc2}",
            event_type="my_event", location='Islamabad',
            event_details="event_details")

        event.save()
        event.keybase.add(keybase)
        # Checking the saved data
        # self.assertEqual(Individual.date_of_birth, "2020-11-27")
        self.assertEqual(individual.gender, "male")
        self.assertEqual(individual.religion, 'islam')
        self.assertEqual(individual.sect, "abc")
        self.assertEqual(group.group_type, "my_group")
        self.assertEqual(group.region, 'Islamabad')
        self.assertEqual(group.details, 'group_details')
        self.assertEqual(event.event_type, "my_event")
        self.assertEqual(event.location, 'Islamabad')
        self.assertEqual(event.event_details, 'event_details')

    @classmethod
    def setUpTestData(cls):
        # store the password to login later

        # Test User create for testing
        password = 'mypassword'
        my_admin = User.objects.create_superuser(
            'myuser',
            'myemail@test.com', password)
        c = Client()
        # You'll need to log him in before
        # you can send requests through the client
        c.login(username=my_admin.username, password=password)
        user_test = User.objects.get(username='myuser')
        keybase = Keybase.objects.get(id=1)
        individual = Individual.objects.create(
            user=user_test,
            title='individuals_title',
            created_on='2020-11-27 07:09:19.000000',
            updated_on='2020-11-27 07:09:19.000000',
            expire_on='2020-11-27 09:09:19.000000',
            addresses="{dummy address1,dummy address2}",
            phone_numbers="{090078601,12345578911}",
            descriptions="{desc1,desc2}",
            date_of_birth='2020-11-27', gender='male',
            religion='islam', sect="abc", )

        individual.save()
        individual.keybase.add(keybase)
        print(individual.id)
        # Test Models For Group
        group = Group.objects.create(
            user=user_test, title='group_title',
            created_on='2020-11-27 07:09:19.000000',
            updated_on='2020-11-27 07:09:19.000000',
            expire_on='2020-11-27 09:09:19.000000',
            addresses="{dummy address1,dummy address2}",
            phone_numbers="{090078601,12345578911}",
            descriptions="{desc1,desc2}",
            group_type="my_group", region='Islamabad',
            details="group_details")
        group.save()
        group.keybase.add(keybase)
        print(group.id)
        # Test Models For Event
        event = Event.objects.create(
            user=user_test, title='event_title',
            created_on='2020-11-27 07:09:19.000000',
            updated_on='2020-11-27 07:09:19.000000',
            expire_on='2020-11-27 09:09:19.000000',
            addresses="{dummy address1,dummy address2}",
            phone_numbers="{090078601,12345578911}",
            descriptions="{desc1,desc2}",
            event_type="my_event", location='Islamabad',
            event_details="event_details")

        event.save()
        event.keybase.add(keybase)
        print(event.id)

    def test_model_get(self):
        individuals = Individual.objects.get(id=1)
        self.assertEqual(individuals.title, 'individuals_title')
        self.assertIsInstance(individuals, Individual)
        group = Group.objects.get(id=1)
        self.assertEqual(group.title, 'group_title')
        self.assertIsInstance(group, Group)
        event = Event.objects.get(id=1)
        self.assertEqual(event.title, 'event_title')
        self.assertIsInstance(event, Event)

    def test_model_edit(self):
        individuals = Individual.objects.filter(id=1).update(
            gender='female',
            religion='hinduism', sect="def")
        print(individuals)

        edited_individuals = Individual.objects.first()
        # self.assertEqual(edited_individuals.date_of_birth, '2020-12-27')
        self.assertEqual(edited_individuals.gender, 'female')
        self.assertEqual(edited_individuals.religion, 'hinduism')
        self.assertEqual(edited_individuals.sect, 'def')

        group = Group.objects.filter(id=1).update(
            group_type="my_group_updated",
            region='Lahore',
            details="group_details_updated")
        print(group)

        edited_group = Group.objects.first()
        self.assertEqual(edited_group.group_type, "my_group_updated")
        self.assertEqual(edited_group.region, "Lahore")
        self.assertEqual(edited_group.details, 'group_details_updated')

        event = Event.objects.filter(id=1).update(
            event_type="my_event_updated", location='Lahore',
            event_details="event_details_updated")
        print(event)

        edited_event = Event.objects.first()
        self.assertEqual(edited_event.event_type, "my_event_updated")
        self.assertEqual(edited_event.location, "Lahore")
        self.assertEqual(edited_event.event_details, 'event_details_updated')

    def test_model_delete(self):
        _, individual_dict = Individual.objects.get(id=1).delete()[1].values()
        print(individual_dict)
        self.assertEqual(individual_dict, 1)
        _, group = Group.objects.get(id=1).delete()[1].values()
        self.assertEqual(group, 1)
        _, event = Event.objects.get(id=1).delete()[1].values()
        self.assertEqual(event, 1)
