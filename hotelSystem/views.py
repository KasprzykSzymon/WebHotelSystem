from django.shortcuts import render

def homePage(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    
    return  render(request, 'homePage.html', context)
