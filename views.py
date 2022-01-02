from framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None))


class Category:
    def __call__(self, request):
        return '200 OK', render('category.html', date=request.get('date', None))


class Admin:
    def __call__(self, request):
        return '200 OK', render('admin.html', date=request.get('date', None))
