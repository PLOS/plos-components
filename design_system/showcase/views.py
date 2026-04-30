from django.shortcuts import render


def text_input_view(request):
    return render(request, "showcase/text_input.html")
