#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth.models import User
import django
from datetime import *
import os
import csv
from django.db import connection
from django.db.models import get_app, get_models
from django.db.models import Q
from pms.settings import *
from django.db import connection
from django.contrib.auth.models import Group, Permission
import pdb

class Command(BaseCommand):

    """ Command To generate Data Entry Operators History in csv format."""

    def handle(self, *args, **options):
        #pdb.set_trace()
        scriptStartTime = datetime.now()
        # add required app names in contentList
        contentList = ['client','projects', 'milestones','people','documents','mastermodule','tasks','times']
        for appname in contentList:
            print scriptStartTime
            appmodels = ContentType.objects.filter(app_label = appname)
            for i in appmodels:
                # to give permissions
                content_type = ContentType.objects.get(app_label = i.app_label, model = i.model)
                print i.app_label,"======",i.model
                
                codename = "can_view_%s" %(i.model)
                name = "Can View %s"%(i.model)
                permission, created = Permission.objects.get_or_create(codename=codename, 
                                    name=name, 
                                    content_type=content_type)
                if created:
                    print "Permission:: %s created for %s " %(permission.codename, i.model)
        print 'Time taken: %s' %(datetime.now() - scriptStartTime)

