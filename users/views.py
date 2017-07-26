from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from warrant import Cognito
from forms import SignUpForm
import awsdata 


def isFBUID(username):
    return username.isdigit() and (len(username) == 16 or len(username) == 17)

def completeUserRegistration(form):
        cognito = Cognito(
            settings.COGNITO_USER_POOL_ID,
            settings.COGNITO_APP_ID)
        cognito.register(form.cleaned_data['username'], form.cleaned_data['password1'], email='dummy@aquaint.us')

    
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/user/' + request.user.username)
    return render(request, 'users/displayuser.html', {'error':1})

# def user_authentication(request):
#     return render(request, 'users/userlogin.html')

def user_signup(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignUpForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print 'User signup form valid.'
            print form.cleaned_data

            #completeUserRegistration(form)

            print 'User signing up done.'
            # redirect to a new URL:
            return HttpResponseRedirect('/user/' + form.cleaned_data['username'])
        else:
            print 'User signup form invalid.'
    else:
        form = SignUpForm()

    return render(request, 'users/usersignup.html', {'form': form})


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
