from flask.ext.tuktuk.helpers import DotExpandedDict, Attribute


class Project(DotExpandedDict):
    """
    :type latest_build: Build
    :type id: int
    :type name: str
    """
    latest_build = Attribute('latest_build')
    id = Attribute('id')
    name = Attribute('name')


class User(DotExpandedDict):
    """
    :type login: str
    :type id: int
    """
    login = Attribute('login')
    id = Attribute('id')

