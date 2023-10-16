import csv
import os
from django.conf import settings
from college.models import College
from student.models import Student
from users.models import UserDetail, User
import random
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText
from email.utils import formatdate
import time

#

colleges_codes_list = [978, 1128, 1025, 607, 1027, 1067, 1151, 720, 886, 581, 649, 650, 746, 747, 778, 844, 874, 479,
                       507, 480, 496, 521, 523, 530, 532, 533, 520, 537, 558, 572, 550, 556, 600, 975, 594, 610, 629,
                       630, 632, 623, 633, 1010, 608, 627, 611, 619, 622, 1045, 669, 657, 639, 673, 643, 653, 1043, 663,
                       694, 700, 699, 702, 686, 690, 687, 706, 719, 709, 1109, 740, 722, 718, 763, 768, 752, 754, 756,
                       757, 758, 761, 771, 765, 1141, 784, 785, 790, 796, 780, 804, 799, 798, 818, 813, 850, 483, 578,
                       651, 645, 681, 682, 825, 1005, 1146, 868, 925, 924, 930, 903, 911, 905, 939, 945, 955, 963, 938,
                       943, 983, 1004, 980, 1002, 996, 981, 1024, 1052, 1028, 1057, 1031, 1033, 1035, 1046, 1077, 1087,
                       1081, 1085, 1127, 1130, 1094, 1096, 1102, 1119, 1115, 1104, 1125, 1159, 1136, 1158, 1134, 1149,
                       1140]
colleges_list = College.objects.filter(status=1, college_code__in=colleges_codes_list).exclude(email=None)
print("total colleges to which we have to send mail ", colleges_list.count())
