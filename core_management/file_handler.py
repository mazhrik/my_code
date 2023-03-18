from core_management.sftp_upload import FTP_Client
from pathlib import Path


def ftp_client_object():
    try:
        client = FTP_Client()
        status = 'client'
        return client, status
    except Exception as ex:
        client = None
        return client, ex


def file_upload_handler(dir_pick_path, folder_name=None, app_name=None):
    try:
        if all(v is not None for v in [dir_pick_path, folder_name, app_name]):
            client, status = ftp_client_object()
            if status == 'client':
                client.upload_directory(directory_pick_path=dir_pick_path,
                                        directory_drop_path=folder_name)
                print("uploadeed ________------------")
                status = 'uploaded'
                url = '/{0}/{1}/'.format(folder_name, folder_name)
            else:
                url = ""
                status = "no client"
                print("---------not working ---------")
        else:
            status = 'no argument'
            url = ""
        return url, status, None
    except Exception as ex:
        status = 'error'
        url = None
        return url, status, ex




def file_upload_handler_frs(dir_pick_path, folder_name=None, app_name=None):
    print("file_upload_handler_frs")
    print(dir_pick_path)
    print(folder_name)
    print(app_name)
    try:
        if all(v is not None for v in [dir_pick_path, folder_name, app_name]):
            client, status = ftp_client_object()
            if status == 'client':
                client.upload_file(dir_pick_path,
                                        folder_name, file_drop_path=app_name)
                print("----------uploaded gand-----------")
                status = 'uploaded'
                url = '/{0}/{1}/'.format(folder_name, folder_name)
            else:
                url = ""
                status = "no client"
                print("---------not working ---------")
        else:
            status = 'no argument'
            url = ""
        return url, status, None
    except Exception as ex:
        status = 'error'
        url = None
        return url, status, ex

