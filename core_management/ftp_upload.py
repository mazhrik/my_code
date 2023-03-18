import ftplib
import os
from urllib.parse import urljoin


class FtpFileTransferException(Exception):
    pass


class FtpFileTransfer:
    """FTP File Server """

    def __init__(self, hostname,
                 username, password, port, remote_root_path):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.path = remote_root_path
        self.connection = None

    # Connection initialized
    def start_connection(self):
        # Check if connection is still alive and if not, drop it.
        if self.connection is not None:
            try:
                self.connection.pwd()
                return 'Connection Resumed'
            except ftplib.all_errors:
                self.connection = None

        # Real reconnect
        if self.connection is None:
            ftp = ftplib.FTP()
            try:
                ftp.connect(self.hostname, self.port)
                ftp.login(self.username, self.password)
                if self.path != '':
                    print(self.path)
                    ftp.cwd(self.path)
                self.connection = ftp
                return 'Connection Established'
            except ftplib.all_errors:
                raise FtpFileTransferException(
                    'Connection or login error using data %s'
                    % repr(self.connection)
                )

    def disconnect(self):
        self.connection.quit()
        self.connection = None

    def make_directory(self, path):
        initial_pwd = self.connection.pwd()
        path_splitted = path.split('/')
        for path_part in path_splitted:
            try:
                print(path_part)
                self.connection.cwd(path_part)
                # return 'Directory already Exist'
            except ConnectionError:
                try:
                    self.connection.mkd(path_part)
                    self.connection.cwd(path_part)
                    # return 'New Directory Created'
                except ftplib.all_errors:
                    raise FtpFileTransferException(
                        'Cannot create directory chain %s' % path
                    )
        self.connection.cwd(initial_pwd)
        return True

    def exists(self, name):
        self.start_connection()
        try:
            nlst = self.connection.nlst(
                os.path.dirname(name) + '/'
            )
            if name in nlst or os.path.basename(name) in nlst:
                return True
            else:
                return False
        except ftplib.error_temp:
            return False
        except ftplib.error_perm:
            # error_perm: 550 Can't find file
            return False
        except ftplib.all_errors:
            raise FtpFileTransferException('Error when testing existence of %s'
                                           % name)

    def upload_file(self, name, content):
        # Connection must be open!
        try:
            initial_pwd = self.connection.pwd()
            self.make_directory(name)
            self.connection.cwd(name)
            self.connection.storbinary('STOR ' + content.name,
                                       content)
            self.connection.cwd(initial_pwd)
        except ftplib.all_errors:
            raise FtpFileTransferException('Error writing file %s' % name)

    def url(self, basepath, appname, filename):
        if self.path is None:
            raise ValueError("This file is not accessible via a URL.")
        path = urljoin(basepath, self.path).replace('\\', '/')
        filepath = urljoin(path, appname).replace('\\', '/')
        return urljoin(filepath, filename).replace('\\', '/')


# Parameters set
#HOSTNAME = '192.168.18.33'
#USERNAME = 'microcrawler'
##PASSWORD = 'rapidev'
#PORT = 21
#BASE_PATH = '/var/www/html/osint_system/media_files/'
#OBJECT_PATH = '67b12f8aecd4c7df578858b0/'
#APP_NAME = 'cms/'
#filename = '/home/waleedusman/Downloads/icon.png'
#FILE_TO_UPLOAD = open(filename, 'rb')


#file_object = FtpFileTransfer(hostname=HOSTNAME, username=USERNAME, password=PASSWORD, port=PORT, remote_root_path=APP_NAME)
#connection_string = file_object.start_connection()
#print(connection_string)
#connection_string = file_object.start_connection()
#print(connection_string)
#directory_string = file_object.make_directory(OBJECT_PATH)
#print(directory_string)
#file_object.upload_file(OBJECT_PATH,FILE_TO_UPLOAD)
#print(file_object.url(BASE_PATH, OBJECT_PATH, FILE_TO_UPLOAD.name))
