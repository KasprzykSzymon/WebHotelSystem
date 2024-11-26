from django.shortcuts import render

def homePage(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return  render(request, 'homePage.html', context)

def lastMinute(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'lastMinute.html', context)

def news(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'news.html', context)


def contact(request):
    return render(request, 'contact.html')

def signIn(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'signIn.html', context)

def searchRoom(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'searchRoom.html')