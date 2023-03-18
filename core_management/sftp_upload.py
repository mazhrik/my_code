"""
SFTP client custom extended module
VERSION 1.1

"""

import os.path, os
from ftplib import FTP, error_perm

from requests.models import Response

from OCS_Rest.settings import FILE_SERVER, USERNAME, PASSWORD, PORT

HOST = FILE_SERVER
PORT = PORT
USERNAME = USERNAME
PASSWORD = PASSWORD

# add base path, without any forward slash on front or back
BASE_PATH = 'cms'  # path we are sure alread exist

# ftp = FTP()

# ftp.login('microcrawler','rapidev')
filenameCV = "/home/rapidev/PycharmProjects/webserver_client/fb_content/"


class FTP_Client(object):

    def __init__(self):
        self.ftp = FTP()

    def connect(self):

        try:
            self.ftp.connect(HOST, PORT)
            return True

        except error_perm as e:
            print(e)
            return False

    def login(self):
        try:
            self.connect()
            self.ftp.login(USERNAME, PASSWORD)
            return True
        except error_perm as e:
            print(e)
            return False

    def quit(self):
        try:

            self.ftp.quit()
            return True
        except error_perm as e:
            print(e)
            return False

    def directory_exists(self, dir):
        filelist = []
        self.ftp.retrlines('LIST', filelist.append)
        print(filelist)

        for f in filelist:
            if f.split()[-1] == dir and f.upper().startswith('D'):
                return True
        return False

    def chdir(self, dir):
        if self.directory_exists(dir) is False:
            self.ftp.mkd(dir)
        self.ftp.cwd(dir)

    def get_parent_directory_path(self, path):
        # return directory's parent directory
        path_list = path.split('/')
        path_list = list(filter(lambda i: len(i) > 0, path_list))

        del (path_list[-1])
        return '/'.join(path_list)

    def create_directory_path(self, path):
        temp_path = ''
        temp_path_list = []

        try:
            path_list = path.split('/')
            path_list = list(filter(lambda i: len(i) > 0, path_list))

            for dir in path_list:
                temp_path = temp_path + dir + '/'
                temp_path_list.append(temp_path)
                self.chdir(dir)  # change to directory if not exist create one

            # print(temp_path_list)

        except Exception as e:
            print(e)
            print(temp_path_list)

    def upload_file(self, file_pick_path, filename, file_drop_path=''):
        if (self.login()):
            try:
                self.chdir(BASE_PATH)
                self.create_directory_path(file_drop_path)
                self.upload_f(file_pick_path, filename)
                return f"{HOST}/{file_drop_path}"

            except error_perm as e:
                print(e)
                return False

        self.quit()
        return True

    def get_host_path(self):
        return str(HOST + "/osint_system/media_files/cms")

    def upload_directory(self, directory_pick_path, directory_drop_path=''):
        if (self.login()):
            try:
                self.chdir(BASE_PATH)
                self.create_directory_path(directory_drop_path)
                self.upload(directory_pick_path)

            except error_perm as e:
                print(e)
                return False

        self.quit()
        return True

    def upload_f(self, file_pick_path, filename):
        if os.path.isfile(os.path.join(file_pick_path, filename)):
            print("STOR", filename)
            self.ftp.storbinary('STOR ' + filename, open(os.path.join(file_pick_path, filename), 'rb'))

    def upload(self, directory_pick_path):

        for name in os.listdir(directory_pick_path):
            localpath = os.path.join(directory_pick_path, name)
            if os.path.isfile(localpath):
                print("STOR", name, localpath)
                self.ftp.storbinary('STOR ' + name, open(localpath, 'rb'))
            elif os.path.isdir(localpath):
                print("MKD", name)

                try:
                    self.ftp.mkd(name)

                # ignore "directory already exists"
                except error_perm as e:
                    if not e.args[0].startswith('550'):
                        raise

                print("CWD", name)
                self.ftp.cwd(name)
                self.upload(localpath)
                print("CWD", "..")
                self.ftp.cwd("..")


    def delete_dir_file(self, GTR):
        try:
            directory = '/ess/'+ GTR    

            # delete files in dir
            files = list(self.ftp.nlst(directory))
            print(len(files))
            for f in files:
                self.ftp.delete(f)
            check = self.ftp.rmd(directory)
            # delete this dir
            return check
            # if check:
            #     return Response({"message":"Successfully deleted",
            #                     "result": str(check)})
        except Exception as e:
            return str(e)
