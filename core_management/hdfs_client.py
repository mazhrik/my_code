from pywebhdfs.webhdfs import PyWebHdfsClient
from OCS_Rest.settings import HDFS_PORT, HDFS_HOST, HDFS_PASSWORD, HDFS_USERNAME, HDFS_ROOT_PATH
import json

# HDFS CONFIGURATION
HOST = HDFS_HOST
PORT = HDFS_PORT
USERNAME = HDFS_USERNAME
HDFS_PASSWORD = HDFS_PASSWORD


class HDFSClient:

    def __init__(self):
        self.hdfs = PyWebHdfsClient(host=HOST, port=PORT, user_name=USERNAME, timeout=200)

    def makdir(self, dir_to_store):
        self.hdfs.make_dir(dir_to_store)

    def create_file(self, data=None, dir_to_store="", file_name=""):
        a_file = f"{dir_to_store}/{file_name}"

        x = self.hdfs.create_file(a_file, json.dumps(data))
        return x

    # list the contents of the directory
    def list_dir(self, dir_name):
        return self.hdfs.list_dir()

    def delete_file(self, file_name):
        return self.hdfs.delete_file_dir(path=file_name, recursive=False)

    def rename_dir(self, old_name, new_name):
        return self.hdfs.rename_file_dir(old_name, new_name)

    def read_file(self, file_dir):
        return self.hdfs.read_file(file_dir)

    def append_file(self, file_dir, data):
        return self.hdfs.append_file(file_dir, data)


def send_file(dir_to_store, data_to_store, case_name):
    try:
        a_file = f"{dir_to_store}{case_name}"
        print('path', a_file)
        print('data to store', data_to_store)
        hdfs_object = HDFSClient()
        created = hdfs_object.hdfs.create_file(a_file, data_to_store, overwrite=True)
        print("created = ", created)
    except Exception as ex:
        print("exceptions e ------",ex)
        return ex


def delete_file_hdfs(dir_to_store, file_name):
    try:
        a_file = f"{dir_to_store}{file_name}"
        print('path', dir_to_store)
        print('path', a_file)
        hdfs_object = HDFSClient()
        print(hdfs_object)
        hdfs_object = HDFSClient()
        hdfs_object.delete_file(a_file)
        return True
    except Exception as ex:
        return False
