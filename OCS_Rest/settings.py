# in production make debug = False
SERVER = 'DEV'

if SERVER == 'DEV':
    from OCS_Rest.dev import *
# elif SERVER == 'PRO':
#     from OCS_Rest.pro import *
# elif SERVER == 'DEMO':
#     from OCS_Rest.demo import *
