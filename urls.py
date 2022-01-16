from datetime import date
from views import Index, Contact, Admin, Products, Examples


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/contacts/': Contact(),
    '/admin/': Admin(),
    '/products/': Products(),
    '/examples/': Examples(),
}
