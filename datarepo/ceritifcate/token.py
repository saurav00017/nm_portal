import jwt
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from skillofferings.models import SKillOfferingEnrollmentCertificate


def get_certificate_token(certificate: SKillOfferingEnrollmentCertificate):
    expire = timezone.now() + timedelta(minutes=5)
    data = {
        'id': certificate.id,
        'certificate_id': certificate.certificate_id,
        'certificate_no': certificate.certificate_no,
        'exp': expire,
    }
    token = jwt.encode(data, settings.CERTIFICATE_TOKEN_KEY, algorithm="HS256")
    return token


def get_certificate_path_from_token(token):
    payload = jwt.decode(token, settings.CERTIFICATE_TOKEN_KEY, algorithms=["HS256"])
    _id = payload.get('id', None)
    _certificate_id = payload.get('certificate_id', None)
    _certificate_no = payload.get('certificate_no', None)
    if _id and _certificate_id and _certificate_no:
        try:
            record = SKillOfferingEnrollmentCertificate.objects.get(id=_id)
            if record.certificate_id == _certificate_id and record.certificate_no == _certificate_no:
                return record.certificate.url if record.certificate else None
        except Exception as e:
            print("Error", e)
    return None

