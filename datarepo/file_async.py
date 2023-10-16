import socket
import paramiko
from scp import SCPClient
from celery import shared_task
import os

SCP_ADDRESSES = {
    '10.236.220.204': '10.236.220.227',
    '10.236.220.227': '10.236.220.204',
}


def current_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

from django.conf import settings

def sync_file_with_scp(file):
    if file:
        ip_address = current_ip()
        if ip_address in SCP_ADDRESSES:
            server = SCP_ADDRESSES[ip_address]
            port = 22
            user = password = 'cloud'

            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server, port, user, password)
            try:
                with SCPClient(client.get_transport()) as scp:
                    folder_path = '/opt/nm/NM_portal_backend/nm_portal'
                    if file:
                        file_path = folder_path + str(file.url)
                        scp.put(file_path, file_path)
                return True
            except Exception as e:
                with open(os.path.join(settings.BASE_DIR, 'datarepo/check_file_sync.csv'), 'a') as file:
                    file.write(f"\n{server},{file.url},Error-{e}")
                print("sync_file_with_scp", e)
        return False


def sync_file_with_scp_with_path(path):
    if path:
        ip_address = current_ip()
        if ip_address in SCP_ADDRESSES:
            server = SCP_ADDRESSES[ip_address]
            port = 22
            user = password = 'cloud'

            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server, port, user, password)
            try:
                with SCPClient(client.get_transport()) as scp:
                    folder_path = '/opt/nm/NM_portal_backend/nm_portal'
                    if path:
                        file_path = folder_path + '/' + str(path)
                        scp.put(file_path, file_path)
                return True
            except Exception as e:
                with open(os.path.join(settings.BASE_DIR, 'datarepo/check_file_sync.csv'), 'a') as file:
                    file.write(f"\n{server},{file.url},Error-{e}")
                print("sync_file_with_scp", e)
        return False
