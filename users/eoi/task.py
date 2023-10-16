
import socket
import paramiko
from scp import SCPClient
from celery import shared_task
from ..models import EOIDetail
import os
SCP_ADDRESSES = {
    '10.236.220.204': '10.236.220.227',
    '10.236.220.227': '10.236.220.204',
}


def current_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


@shared_task
def async_scp_with_eoi_files(eoi_detail_id):
    eoi_details = EOIDetail.objects.get(id=eoi_detail_id)
    ip_address = current_ip()
    if ip_address in SCP_ADDRESSES:
        server = SCP_ADDRESSES[ip_address]
        port = 22
        user = password = 'cloud'

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        with SCPClient(client.get_transport()) as scp:
            folder_path = '/opt/nm/NM_portal_backend/nm_portal'
            if eoi_details.registration_document:
                file_path = folder_path + str(eoi_details.registration_document.url)
                scp.put(file_path, file_path)
            if eoi_details.detailed_proposal_document:
                file_path = folder_path + str(eoi_details.detailed_proposal_document.url)
                scp.put(file_path, file_path)
            if eoi_details.declaration_document:
                file_path = folder_path + str(eoi_details.declaration_document.url)
                scp.put(file_path, file_path)
        return True
    return False
