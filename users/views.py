from django.shortcuts import render
from django.http import HttpResponse
import awsdata 


def isFBUID(username):
    return username.isdigit() and (len(username) == 16 or len(username) == 17)

def index(request):
    return render(request, 'users/displayuser.html', {'error':1}) 
# Create your views here.
def info(request, user):
    data = awsdata.get_user_data(user)
    fb_company = ''
    ios_url = ''
    android_url = ''

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
                    if not values[valIndex].startswith('company/'):
                        data.accounts[key][valIndex] = "profile/view?id=" + values[valIndex]
                if key == "facebook":
					# Differentiate users and companies by detecting fbuids
                    if not isFBUID(values[valIndex]): 
                        fb_company = values[valIndex] 
                # Only display first iOS and android app
                if key == "ios":
                    ios_url = data.accounts[key][0]
                    data.accounts.pop(key)
                if key == "android":
                    android_url = data.accounts[key][0]
                    data.accounts.pop(key)
    context = {
        'error':0,
        'username':user,
        'realname':data.realname,
        'accounts':data.accounts,
        'isprivate':data.isprivate,
        'scancodeimgurl':data.scancodeimgurl,
        'fbcompany': fb_company,
        'iosurl': ios_url,
        'androidurl': android_url 
    }
    return render(request, 'users/displayuser.html', context)
