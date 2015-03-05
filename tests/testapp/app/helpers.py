from flask.ext.tuktuk.helpers import DotExpandedDict, Attribute


class User(DotExpandedDict):
    """
    :type login: str
    :type id: int
    """
    def __init__(self, login=None, id=None):
        super(User, self).__init__(login=login, id=id)
    login = Attribute('login')
    id = Attribute('id')


class Project(DotExpandedDict):
    """
    :type id: int
    :type name: str
    """
    latest_build = Attribute('latest_build')
    id = Attribute('id')
    name = Attribute('name')


class IdReference(DotExpandedDict):
    """
    :type id: int
    """
    def __init__(self, id=None):
        super(IdReference, self).__init__(id=id)
    id = Attribute('id')


class UserCollection(DotExpandedDict):
    """
    :type items: list[User]
    :type length: int
    :type total: int
    :type offset: int
    """
    # TODO autogenerate constructors
    def __init__(self, id=None, items=None, total=None, offset=None):
       super(UserCollection, self).__init__(id=id, items=items, total=total, offset=offset)

    items = Attribute('items')
    length = Attribute('length')
    total = Attribute('total')
    offset = Attribute('offset')

