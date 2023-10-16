import csv
import os
import uuid
import json
from django.conf import settings
from skillofferings.models import Specialisation, SKillOffering, SKillOfferingEnrollment, \
    SKillOfferingEnrollmentProgress
from skillofferings.models import KnowledgePartner, Technology, SubTechnology
from datarepo.models import Branch, YearOfStudy
import time

file = open(os.path.join(settings.BASE_DIR, 'scripts/courses/f1_free_courses.csv'), 'r')
csv_data = csv.reader(file)
counter = 0
for record in csv_data:
    time.sleep(0.5)
    print(record)
    new_kp = None
    # training partner
    try:
        new_kp = KnowledgePartner.objects.get(
            name=record[0],
        )
    except KnowledgePartner.DoesNotExist:
        new_kp = KnowledgePartner.objects.create(
            name=record[0],
        )
        new_kp.save()

    new_tech = None
    try:
        new_tech = Technology.objects.get(
            name=record[1],
        )
    except Technology.DoesNotExist:
        new_tech = Technology.objects.create(
            name=record[1],
        )
        new_tech.save()

    # course_name

    new_sub_tech = None
    try:
        new_sub_tech = SubTechnology.objects.get(
            tech_id=new_tech.id,
            name=record[3],
        )
    except SubTechnology.DoesNotExist:
        new_sub_tech = SubTechnology.objects.create(
            tech_id=new_tech.id,
            name=record[3],
        )
        new_sub_tech.save()

    new_Skil_offering = SKillOffering.objects.create(
        knowledge_partner_id=new_kp.id,
        technology_id=new_tech.id,
        course_name=record[2],
        sub_technology_id=new_sub_tech.id,
        mode_of_delivery=record[8],
        duration=record[9],
        outcomes=record[10],
        course_content=None,
        description=None,
        certification=record[11],
        cost=record[13],
        link=record[14],
        is_mandatory=0,
        offering_type=0 if record[8].lower() == 'offline' else 1,
        offering_kind=0,
        job_category=record[12],
    )
    new_Skil_offering.save()

    specialization_info = Specialisation.objects.get(id=int(record[4]))
    new_Skil_offering.specialization.add(specialization_info)
    new_Skil_offering.save()

    branches = record[6].split(',')
    if len(branches) == 0:
        all_branchs = Branch.objects.all()
        for branch in all_branchs:
            new_Skil_offering.branch.add(branch)
            new_Skil_offering.save()
    elif len(branches) >= 1:
        for branch in branches:
            try:
                new_branch = Branch.objects.get(
                    name=branch,
                )
                new_Skil_offering.branch.add(new_branch)
                new_Skil_offering.save()
            except Branch.DoesNotExist:
                new_branch = Branch.objects.create(
                    name=branch,
                )
                new_branch.save()
                new_Skil_offering.branch.add(new_branch)
                new_Skil_offering.save()

    years = record[7].split(',')
    for year in years:
        if year.lower() == 'any':
            all_years = YearOfStudy.objects.all()
            for year in all_years:
                new_Skil_offering.year_of_study.add(year)
                new_Skil_offering.save()
        elif year == '':
            pass
        else:
            try:
                new_year = YearOfStudy.objects.get(
                    year=year,
                )
                new_year.save()
                new_Skil_offering.year_of_study.add(new_year)
                new_Skil_offering.save()
            except YearOfStudy.DoesNotExist:
                new_year = YearOfStudy.objects.create(
                    year=year,
                )
                new_year.save()
                new_Skil_offering.year_of_study.add(new_year)
                new_Skil_offering.save()
