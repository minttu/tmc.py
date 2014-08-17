import os

from peewee import (BooleanField, CharField, DateField, ForeignKeyField,
                    IntegerField, Model, SqliteDatabase, DoesNotExist)
from tmc.errors import NoCourseSelected, NoExerciseSelected

# SqliteDatabase will fail if there is no ~/.config
if not os.path.isdir(os.path.join(os.path.expanduser("~"), ".config")):
    os.mkdir(os.path.join(os.path.expanduser("~"), ".config"), 0o700)

sqlite = SqliteDatabase(
    os.path.join(os.path.expanduser("~"), ".config", "tmc.db")
)
sqlite.connect()


class BaseModel(Model):

    class Meta:
        database = sqlite


class Course(BaseModel):
    tid = IntegerField(unique=True)
    name = CharField()
    is_selected = BooleanField(default=False)
    path = CharField(default="")

    def set_select(self):
        Course.update(
            is_selected=False
        ).where(Course.is_selected == True).execute()
        self.is_selected = True
        self.save()

    @staticmethod
    def get_selected():
        selected = Course.select().where(Course.is_selected == True).first()
        if not selected:
            raise NoCourseSelected()
        return selected

    def __str__(self):
        return "Course \"{}\" (ID {})".format(self.name, self.tid)

    def __repr__(self):
        return str(self)

    def menuname(self):
        return self.name


class Exercise(BaseModel):
    tid = IntegerField(unique=True)
    name = CharField()
    course = ForeignKeyField(Course, related_name="exercises")
    is_selected = BooleanField(default=False)
    is_completed = BooleanField(default=False)
    is_downloaded = BooleanField(default=False)
    is_attempted = BooleanField(default=False)
    deadline = DateField(null=True)

    def get_course(self):
        return Course.get(Course.id == self.course)

    def path(self):
        course = Course.get(Course.id == self.course)
        return os.path.join(course.path, "/".join(self.name.split("-")))

    def set_select(self):
        Exercise.update(is_selected=False).where(
            Exercise.is_selected == True).execute()
        self.is_selected = True
        self.course.set_select()
        self.save()

    def update_downloaded(self):
        self.is_downloaded = os.path.isdir(self.path())
        self.save()

    @staticmethod
    def get_selected():
        is_selected = Exercise.select().where(Exercise.is_selected == True)
        first = None
        for item in is_selected:
            first = item
            break
        if not first:
            raise NoExerciseSelected()
        return first

    @staticmethod
    def byid(id):
        return Exercise.get(Exercise.tid == int(id))

    def __str__(self):
        return "Exercise \"{}\" (ID {})".format(self.name, self.tid)

    def __repr__(self):
        return str(self)

    def menuname(self):
        short, rest = "", ""
        if "-" in self.name:
            rest = self.name.split("-")[-1]
        else:
            rest = self.name
        if "." in rest:
            split = rest.split(".")
            short = split[-1]
            rest = ".".join(split[0:-1])
        realname = ""
        for c in short:
            if c.isupper():
                if len(realname) == 0:
                    realname += c
                else:
                    realname += " " + c
            else:
                realname += c
        if len(realname) > 0:
            return rest.replace("_", " - ") + " - " + realname
        return self.name


class Config(BaseModel):
    name = CharField(primary_key=True)
    value = CharField()

    @staticmethod
    def set(name, value):
        try:
            old = Config.get(Config.name == name)
            old.value = value
            old.save()
        except DoesNotExist:
            Config.create(name=name, value=value)

    @staticmethod
    def get_value(name):
        return Config.get(Config.name == name).value

    @staticmethod
    def has():
        try:
            Config.get(Config.name == "url")
            return True
        except DoesNotExist:
            return False


def init_db():
    Course.create_table(fail_silently=True)
    Exercise.create_table(fail_silently=True)
    Config.create_table(fail_silently=True)

init_db()


def reset_db():
    Course.drop_table()
    Exercise.drop_table()
    Config.drop_table()
    init_db()
