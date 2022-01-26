from framework.templator import render
from patterns.сreational_patterns import Engine, Logger, MapperRegistry
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, \
    ListView, CreateView, BaseSerializer
from patterns.unit_of_work_pattern import UnitOfWork

site = Engine()
logger = Logger('main')

routes = {}
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()

UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None))


@AppRoute(routes=routes, url='/contacts/')
class Contact:
    @Debug(name='Contact')
    def __call__(self, request):
        return '200 OK', render('contact.html', date=request.get('date', None))


# контроллер - список продуктов
@AppRoute(routes=routes, url='/product_list/')
class ProductList:
    def __call__(self, request):
        logger.log('Список продуктов')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('product_list.html',
                                    objects_list=category.product,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


# контроллер - создать продукт
@AppRoute(routes=routes, url='/product-list/')
class CreateProduct:
    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                product = site.create_product('milk', name, category)

                product.observers.append(email_notifier)
                product.observers.append(sms_notifier)

                site.product.append(product)

            return '200 OK', render('product_list.html',
                                    objects_list=category.product,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_product.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# контроллер - создать категорию
@AppRoute(routes=routes, url='/examples/')
class CreateCategory:
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('index.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('examples.html',
                                    categories=categories)


# контроллер - список категорий
@AppRoute(routes=routes, url='/products/')
class CategoryList:
    def __call__(self, request):
        return '200 OK', render('product.html',
                                objects_list=site.categories)


# контроллер - копировать курс
@AppRoute(routes=routes, url='/copy-product/')
class CopyProduct:
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_product = site.get_product(name)
            if old_product:
                new_name = f'copy_{name}'
                new_product = old_product.clone()
                new_product.name = new_name
                site.product.append(new_product)

            return '200 OK', render('product_list.html',
                                    objects_list=site.product,
                                    name=new_product.category.name)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@AppRoute(routes=routes, url='/customer-list/')
class CustomerListView(ListView):
    template_name = 'customer_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('customer')
        return mapper.all()


@AppRoute(routes=routes, url='/admin/')
class CustomerCreateView(CreateView):
    template_name = 'admin.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('customer', name)
        site.customer.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/add-product/')
class AddCustomerByProductCreateView(CreateView):
    template_name = 'add_product.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['product'] = site.product
        context['customer'] = site.customer
        return context

    def create_obj(self, data: dict):
        product_name = data['product_name']
        product_name = site.decode_value(product_name)
        product = site.get_product(product_name)
        customer_name = data['customer_name']
        customer_name = site.decode_value(customer_name)
        customer = site.get_customer(customer_name)
        product.add_customer(customer)


@AppRoute(routes=routes, url='/api/')
class CourseApi:
    @Debug(name='CourseApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.product).save()

