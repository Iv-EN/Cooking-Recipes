from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, '404.html', status=HTTPStatus.NOT_FOUND)
