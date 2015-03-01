from flask.ext.tuktuk.helpers import DotExpandedDict, Attribute


class Project(DotExpandedDict):
    """
    :type latest_build: Build
    :type id: numbers.Number
    :type name: str
    """
    latest_build = Attribute('latest_build')
    id = Attribute('id')
    name = Attribute('name')


class Build(DotExpandedDict):
    """
    :type finished_at: str
    :type id: numbers.Number
    :type result: str
    """
    finished_at = Attribute('finished_at')
    id = Attribute('id')
    result = Attribute('result')

