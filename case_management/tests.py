from django.test import TestCase
from case_management.models import (Investigator,
                                    Media, Person,
                                    Location, Evidence,
                                    Case)
from django.contrib.auth.models import User


class LanguageTest(TestCase):
    """
      Language Testcase
      """

    def setUp(self):
        language = Language(name="english", accent="american",
                            can_read=True, can_write=False,
                            can_speak=True,
                            fluency='intermediate')
        language.save()
        language.delete()
        print(language.name)
        self.assertNotEqual(language.name, "dnwidn")
        print("pass")
        self.assertEqual(language.can_speak, True)
        # language.delete()

    def test_language_test(self):
        lang_name = Language(name="english")


class InvestigatorTest(TestCase):
    """
    Investigator Testcase

    """

    def setUp(self):
        u = User(first_name="Ameer")
        u.save()
        user = User.objects.get(first_name="Ameer")

        investigator = Investigator(user=user, first_name="Ameer",
                                    last_name="Hamza", employee_id="1321",
                                    phone=9007986876, cnic=1468415041,
                                    email="a@m.com", investigator_type="tso")
        investigator.save()
        print(" saved ", investigator.last_name)
        self.assertEqual(investigator.first_name, "Ameer")
        self.assertIsInstance(investigator.user, type(user))

    def test_invesigator_test(self):
        name = Investigator(first_name="ameer")


class MediaTest(TestCase):
    """
     Media Testcase

    """

    def setUp(self):
        investigator = Media(media_url="http://media", title="fav",
                             type="Document")
        investigator.save()
        self.assertEqual(investigator.title, "fav")

    def test_invesigator_test(self):
        name = Media.objects.get(title='fav')


class PersonTest(TestCase):
    """
    Person Testcase

    """

    def setUp(self):
        language = Language(name="english", accent="american",
                            can_read=True, can_write=False,
                            can_speak=True,
                            fluency='intermediate')
        language.save()
        lan = Language.objects.get(name="english")

        pic = Media(media_url="http://media", title="fav",
                    type="Document")
        pic.save()
        pict = Media.objects.get(title="fav")
        investigator = Person(first_name="Ameer", last_name="Hamza",
                              description="dfsfawdfasdf", gender="male",
                              phone=9007986876, cnic=1468415041,
                              category="reporter", email="tso@d.com",
                              picture=pict, languages=lan)
        investigator.save()
        self.assertEqual(investigator.first_name, "Ameer")
        self.assertIsInstance(investigator.languages, type(lan))
        self.assertIsInstance(investigator.picture, type(pict))

    def test_invesigator_test(self):
        name = Person.objects.get(email="tso@d.com")


class LocationTest(TestCase):
    """
    Location Testcase

    """

    def setUp(self):
        investigator = Location(address="abc", latitude=10.21,
                                longitude=10.33, description="dfsfawdfasdf",
                                )
        investigator.save()
        self.assertEqual(investigator.latitude, 10.21)

    def test_invesigator_test(self):
        name = Location.objects.get(latitude=10.21)


# class ShapesLocationTest(TestCase):
#     """
#     Investigator Testcase
#
#     """
#
#     def setUp(self):
#         investigator = ShapesLocation(shape_type="tick", latitude=10.21,
#                                       longitude=10.33, description="dfsfawdfasdf",
#                                       radius=0.0, layer_no=0,
#                                       layer_name=""
#                                       )
#         investigator.save()
#
#     def test_invesigator_test(self):
#         name = ShapesLocation.objects.get(shape_type="tick")
#         self.assertEqual(name.latitude, 10.21)


class EvidenceTest(TestCase):
    """
    Evidence Testcase

    """

    def setUp(self):
        loc = Location(address="abc", latitude=10.21,
                       longitude=10.33, description="dfsfawdfasdf",
                       )
        loc.save()
        locate = Location.objects.get(latitude=10.21)

        investigator = Evidence(title="adad", description="dfsfawdfasdf",
                                location=locate, created_on="12 - 10 - 2020",
                                )
        investigator.save()
        self.assertEqual(investigator.title, "adad")
        self.assertIsInstance(investigator.location, type(locate))

    def test_invesigator_test(self):
        name = Evidence.objects.get(title="adad")


class CaseTest(TestCase):
    """
    Case Testcase

    """

    def setUp(self):
        loc = Location(address="abc", latitude=10.21,
                       longitude=10.33, description="dfsfawdfasdf",
                       )
        loc.save()

        locate = Location.objects.get(latitude=10.21)

        evidence = Evidence(title="adad", description="dfsfawdfasdf",
                            location=locate, created_on="12 - 10 - 2020",
                            )
        evidence.save()

        language = Language(name="english", accent="american",
                            can_read=True, can_write=False,
                            can_speak=True,
                            fluency='intermediate')
        language.save()

        lan = Language.objects.get(name="english")

        pic = Media(media_url="http://media", title="fav",
                    type="Document")
        pic.save()
        pict = Media.objects.get(title="fav")
        people = Person(first_name="Ameer", last_name="Hamza",
                        description="dfsfawdfasdf", gender="male",
                        phone=9007986876, cnic=1468415041,
                        category="reporter", email="tso@d.com",
                        picture=pict, languages=lan)
        people.save()

        investigator = Case(case_title="adad", case_cnic=8102125221,
                            case_phone="5454215", is_enabled=True,
                            created_on="2020-10-20", expire_on="2020-10-20",
                            updated_on="2020-10-20", incident_datetime="2020-10-20",
                            case_type="murder", case_description="hhdwd",
                            case_priority="high", case_state="in-progress",
                            locations=locate)

        investigator.save()
        investigator.evidences.add(evidence.id)
        investigator.media.add(pict.id)
        investigator.people.add(people.id)
        self.assertEqual(investigator.case_title, "adad")
        self.assertIsInstance(investigator.locations, type(locate))

    def test_invesigator_test(self):
        name = Case.objects.get(case_title="adad")
