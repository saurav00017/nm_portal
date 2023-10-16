from skillofferings.models import SKillOfferingEnrollment
from skillofferings.models import SKillOffering

nava = SKillOfferingEnrollment.objects.filter(knowledge_partner_id=2,is_mandatory=0)
for x in nava:
    x.knowledge_partner_id = 100
    x.save()
