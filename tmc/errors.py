class TMCError(RuntimeError):

    def __init__(self, value="Undefined TMC Error occured!"):
        self.value = value

    def __str__(self):
        return "\033[31m{0}\033[0m".format(self.value)


class TMCExit(TMCError):

    def __init__(self):
        self.value = "sys.exit"


class WrongExerciseType(TMCError):

    def __init__(self, type):
        self.value = "Exercise wasn't of the type \"{}\".".format(type)


class NoSuitableTestFound(TMCError):

    def __init__(self):
        self.value = "No suitable test was found for the exercise."


class MissingProgram(TMCError):

    def __init__(self, program):
        self.value = "You don't seem to have {} installed.".format(program)


class NotDownloaded(TMCError):

    def __init__(self):
        self.value = "That exercise has not been downloaded!"


class NoSuchExercise(TMCError):

    def __init__(self):
        self.value = "There is no such exercise."


class NoSuchCourse(TMCError):

    def __init__(self):
        self.value = "There is no such course."


class NoCourseSelected(TMCError):

    def __init__(self):
        self.value = "No course has been selected. (tmc select --course)"


class NoExerciseSelected(TMCError):

    def __init__(self):
        self.value = "No exercise has been selected. (tmc select)"


class APIError(TMCError):

    def __init__(self, value="Undefined API error occured!"):
        self.value = value
