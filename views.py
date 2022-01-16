from framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None))


class Contact:
    def __call__(self, request):
        return '200 OK', render('contact.html', date=request.get('date', None))


class Admin:
    def __call__(self, request):
        return '200 OK', render('admin.html', date=request.get('date', None))


class Products:
    def __call__(self, request):
        return '200 OK', render('product.html', date=request.get('date', None))


class Examples:
    def __call__(self, request):
        return '200 OK', render('examples.html', date=request.get('date', None))
