from datarepo.models import Zone

zones_l = [
'ZONE I',
'ZONE II',
'ZONE III', 
'ZONE IV', 
'ZONE V', 
'ZONE XXI', 
'ZONE VI', 
'ZONE VII', 
'ZONE VIII', 
'ZONE IX', 
'ZONE X', 
'ZONE XI', 
'ZONE XII', 
'ZONE XIII', 
'ZONE XVIII', 
'ZONE XIV', 
'ZONE XV', 
'ZONE XXIII', 
'ZONE XVI', 
'ZONE XVII', 
'ZONE XX', 
]

for x in zones_l:
    try:
        zone_i = Zone.objects.get(name=x)
    except Zone.DoesNotExist:
        zone_i = Zone.objects.create(name=x)
        zone_i.save()