from pydatabase.sqlite_interface import SqliteInterface

def test_query_all():

    all_data = [('Football', 'Sporting Goods', 49.99, 1), ('Baseball', 'Sporting Goods', 9.99, 1),
                ('Basketball', 'Sporting Goods', 29.99, 0), ('iPod Touch', 'Electronics', 99.99, 1),
                ('iPhone 5', 'Electronics', 399.99, 0), ('Nexus 7', 'Electronics', 199.99, 1)]

    db = SqliteInterface('data/shop.db')
    queries = db.query(table='items')

    assert queries == all_data


def test_query_display_fields():

    all_names = [('Baseball',), ('Basketball',), ('Football',), ('Nexus 7',), ('iPhone 5',), ('iPod Touch',)]

    db = SqliteInterface('data/shop.db')
    queries = db.query(table='items',display_fields=('name',))

    assert queries == all_names


def test_query_display_two_fields():

    all_names_prices = [('Football', 49.99), ('Baseball', 9.99), ('Basketball', 29.99), ('iPod Touch', 99.99), ('iPhone 5', 399.99), ('Nexus 7', 199.99)]

    db = SqliteInterface('data/shop.db')
    queries = db.query(table='items',display_fields=('name','price'))

    assert queries == all_names_prices


def test_query_primary_key():

    db = SqliteInterface('data/shop.db')
    assert db.primary_key['items'] =='name'


def test_query_numerical():

    data = [('Football', 49.99), ('Baseball', 9.99), ('Basketball', 29.99)]

    db = SqliteInterface('data/shop.db')
    queries = db.query(table='items', display_fields=('name', 'price'), query='price<50')

    assert queries == data