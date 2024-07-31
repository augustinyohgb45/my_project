from django.shortcuts import render

# Create your views here.
def acceuil(request):
    return render(request, 'dashboard/index.html')
def incident(request):
    return render(request, 'dashboard/incident.html')
def changement(request):
    return render(request, 'dashboard/changement.html')