from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail, EmailMessage, BadHeaderError
#from people.models import UserProfile
from django.contrib.auth.models import User
from django.conf import settings
from pms.settings import EMAIL_HOST_USER
print EMAIL_HOST_USER
class Command(BaseCommand):

    """ This is to send mail to all the users based on the locations  """

    def handle(self, *args, **options):
        import ipdb;ipdb.set_trace();
        user_list = User.objects.filter(username__in=['spb'])
        super_body = 'We have sent mail to all the users. Please do have a contact regarding this'
        user_body = 'Please Collect the information and upload it to server'
        for i in user_list:
            if i.is_superuser:
                email = EmailMessage('Dear %s' %(i.get_full_name()), super_body, EMAIL_HOST_USER, [i.email], headers = {'Reply-To':EMAIL_HOST_USER})
                email.send()
                print email
            else:
                email = EmailMessage('Dear %s' %(i.get_full_name()), super_body, EMAIL_HOST_USER, [i.email], headers = {'Reply-To':EMAIL_HOST_USER})
                email.send()
                print email
