from skillofferings.models import SKillOfferingEnrollment
from skillofferings.models import SKillOffering

a = SKillOffering.objects.filter(is_mandatory=1)
for x in a:
    x.offering_type = 1
    x.offering_kind = 1
    x.save()