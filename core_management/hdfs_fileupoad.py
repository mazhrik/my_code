


# from ocs_rest.core_management.models import AutoML
# from rest_framework.response import Response
# from ocs_rest.core_management.hdfs_client import send_file
# from OCS_Rest.settings import HDFS_ROOT_PATH


# from hdfs_client import HDFSClient
# import uuid
# import pandas as pd
# root = 'user/ocs'


# hdfs = HDFSClient()

# # data = 'http://192.168.18.232:8000/v1/portfolio/event/'
# for index,data in enumerate(pd.read_csv('core_management/Document.csv',chunksize=2)):
#     print(type(data))
#     break
#     data = data.to_csv(header=True)
#     filename = f'{str(uuid.uuid1())}.csv'
#     hdfs.create_file(data=data, dir_to_store=root, file_name=filename)
