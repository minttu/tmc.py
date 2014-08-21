# pylint: disable=C0111
from tmc.coloring import as_error


class TMCError(RuntimeError):

    def __init__(self, value="Undefined TMC Error occured!"):
        super().__init__()
        self.value = value

    def __str__(self):
        return as_error(repr(self.value))


class TMCExit(TMCError):

    def __init__(self):
        super().__init__("sys.exit")


class WrongExerciseType(TMCError):

    def __init__(self, ex_type):
        super().__init__("Exercise wasn't of a \"{}\" type.".format(ex_type))


class NoSuitableTestFound(TMCError):

    def __init__(self):
        super().__init__("No suitable test was found for the exercise.")


class MissingProgram(TMCError):

    def __init__(self, program):
        super().__init__("Program {} wasn't found.".format(program))


class NotDownloaded(TMCError):

    def __init__(self):
        super().__init__("That exercise has not been downloaded!")


class NoSuchExercise(TMCError):

    def __init__(self):
        super().__init__("There is no such exercise.")


class NoSuchCourse(TMCError):

    def __init__(self):
        super().__init__("There is no such course.")


class NoCourseSelected(TMCError):

    def __init__(self):
        super().__init__("No course has been selected. (tmc select --course)")


class NoExerciseSelected(TMCError):

    def __init__(self):
        super().__init__("No exercise has been selected. (tmc select)")


class APIError(TMCError):

    def __init__(self, value="Undefined API error occured!"):
        super().__init__(value)
