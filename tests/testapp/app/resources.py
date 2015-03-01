import jsl


class Build(jsl.Document):
    id = jsl.IntField(required=True)
    result = jsl.StringField(enum=('SUCCEDED', 'FAILED'), required=True)
    finished_at = jsl.DateTimeField(required=True)


class Project(jsl.Document):
    id = jsl.IntField(required=True)
    name = jsl.StringField(required=True, min_length=10, max_length=20)
    latest_build = jsl.DocumentField(Build)