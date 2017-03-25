from django.shortcuts import render
from django.http import HttpResponse
import awsdata 

def index(request):
    return render(request, 'users/displayuser.html', {'error':1}) 
# Create your views here.
def info(request, user):
    data = awsdata.get_user_data(user)

    if data == []:
        return render(request, 'users/displayuser.html', {'error':1}) 

    if data.accounts != []:
        # convert accounts to actual url scheme after the .com
        for key, values in data.accounts.items():
            for valIndex in range(len(values)):
                if key == "snapchat":
                    data.accounts[key][valIndex] = "add/" + values[valIndex]
                if key == "tumblr":
                    data.accounts[key][valIndex] = "blog?blogName=" + values[valIndex]
                if key == "linkedin":
                    data.accounts[key][valIndex] = "profile/view?id=" + values[valIndex]

    context = {
        'error':0,
        'username':user,
        'realname':data.realname,
        'accounts':data.accounts,
        'isprivate':data.isprivate,
        'scancodeimgurl':data.scancodeimgurl 
    }
    return render(request, 'users/displayuser.html', context)
