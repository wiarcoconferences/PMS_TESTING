from django.shortcuts import render
from invoice.models import *
from invoice.forms import *
from django.http import HttpResponseRedirect, HttpResponse, Http404


def invoices_details(request):
    invoices = Invoices.objects.all()
    return render(request,"invoice/invoices-home.html",locals())
    
def invoice_add(request):
    msg = ''
    f = ''
    form = InvoicesForm()
    if request.method == "POST":
        form = InvoicesForm(request.POST)
        title = request.POST.get('title','')
        terms = request.POST.get('terms','')
        if form.is_valid():
            f=form.save(commit=False)
            f = form.save()
            msg = 'Invoice is Successfully Generated '
            return HttpResponseRedirect("/invoices-home/")
        else:
            msg = 'Already Exists'
    return render(request,'invoice/invoice.html',locals())
    
def invoice_edit(request,id_edit):
    msg = ''
    f = ''
    invoices = Invoices.objects.get(id=id_edit)
    form = InvoicesForm(instance=invoices)
    if request.POST:
        form = InvoicesForm(request.POST,instance=invoices)
        if form.is_valid():
            f = form.save(commit=False)
            if not Invoices.objects.filter(title=request.POST.get('title')).exclude(id=invoices.id).exists():
                f.save()
                edit_done = True
                msg = "Edited Successfully"
                success = True
            else:
                msg = "Already Exists"
                print "msg"
            return HttpResponseRedirect("/invoices-home/")
        else:
            msg = "Invalid Data"
    return render(request,"invoice/invoice.html",locals())
        
def invoice_delete(request,id_delete):
    invoices = Invoices.objects.get(id=id_delete)
    invoices.delete()
    return render(request,"invoice/invoice.html",locals())
''''     
def invoice_active(request,id_active):
        invoices = Invoices.objects.get(id=id_active)
        invoices.active = 2
        invoices.save()
        success = True
        msg = "Successfully Activated"
    return render(request,"invoice/invoice.html",locals())
    '''
    
    
    
    
def import_data(request):
    key = request.GET.get('key')

    if request.method == "POST":
        #import ipdb;ipdb.set_trace()
        csvfile = ''
        data_file = request.FILES.get('data_file')
        if key == "invoices":
            if data_file:
                csvfile = CSVFiles.objects.create(upload_file=data_file)
                csv_path = ('/home/raju/Desktop/pms/static/') + str(csvfile.upload_file)
                reader=csv.reader(open(csv_path,'rb'), delimiter=';')
                fields=reader.next()
                for i,item in enumerate(reader):
                    items = zip(fields,item)
                    row = {}
                    for (name,value) in items:
                        row[name]=value.strip()
                        pl = Project()
                    for x,y in row.items():
                       setattr(pl,x,y)
                    pl.save()
                msg_upload = "Uploaded Successfully.."
    return render(request,'invoice/import-invoice.html', locals())
