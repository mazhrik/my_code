from django.utils.translation import gettext as _

# Constants used in CASE MANAGEMENT
INVESTIGATOR_TYPE = [('tso', _('Investigator is TSO')),
                     ('tmo', _('Investigator is TMO')),
                     ('pao', _('Investigator is PAO')),
                     ('rdo', _('Investigator is RDO')),
                     ('pdo', _('Investigator is PDO'))
                     ]

CASE_TYPE = [('homicide', _('Case Type is type-1')),
             ('cybercrime', _('Case Type is type-2')),
             ('forensic investigations', _('Case Type is type-3')),
             ('fraud', _('Case Type is type-4')),
             ('family and sexual violence', _('Case Type is type-5')),
             ('crimes against property', _('Case Type is type-6')),
             ('cold cases', _('Case Type is type-7')),
             ('narcotics', _('Case Type is type-8')),
             ('gang violence', _('Case Type is type-9')),
             ('murder', _('Case Type is type-10')),
             ]

CASE_PRIORITY = [('high', _('Case Priority is High')),
                 ('low', _('Case Priority is Low')),
                 ('moderate', _('Case Priority is Moderate')),
                 ]
CASE_STATE = [('pending', _('Case is Pending')),
              ('active', _('Case is Active')),
              ('closed', _('Case is Closed')),
              ]

GENDER = [('male', _('Person is Male')),
          ('female', _('Person is Female'))
          ]

PERSON_TYPE = [('reporter', _('Person is reporter')),
               ('witness', _('Person is witness')),
               ('suspect', _('Person is suspect')),
               ('accused', _('Person is accused')),
               ('victim', _('Person is accused')),
               ('dependent', _('Person is dependent')),
               ('guilty', _('Person is guilty')),
               ('innocent', _('Person is innocent'))
               ]

LANGUAGE = [('mandarin chinese', _('Mandarin Chinese')),
            ('spanish', _('Spanish')),
            ('english', _('English')),
            ('hindi', _('Hindi')),
            ('bengali', _('Bengali')),
            ]

SPOKEN_LANGUAGE_FLUENCY = [('beginner', _('Beginner')),
                           ('elementary', _('Elementary')),
                           ('intermediate', _('Intermediate')),
                           ('upper Intermediate', _('Upper Intermediate')),
                           ('advanced', _('Advanced')),
                           ('proficient', _('Proficient'))
                           ]

MEDIA_TYPE = [('doc', _('Document')),
              ('pic', _('Picture')),
              ('vid', _('Video')),
              ]

APP_PREFIX = "OWL-"
INVESTIGATOR_PREFIX = "TMO-"
