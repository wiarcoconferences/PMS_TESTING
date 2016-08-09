
from django.conf import settings

def add_client_details(sender, **kwargs):

    from client.models import  Test_table_for_sign 
    from people.models import UserProfile
    project = kwargs["instance"]
    import ipdb;ipdb.set_trace();

    client_test_obj = Test_table_for_sign.objects.create(name=project.first_name,
                    address = project.address, 
                        email = project.email
                        )
#    client_test_obj.save()
    for i in project.project.all():
        client_test_obj.project.add(i)
    client_test_obj.save()




