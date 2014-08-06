from tmc.version import __version__ as version

# Username to use
username = "tmc.py"
# password = something here
# What server to test against
server_uri = "https://tmc.mooc.fi/test/"
course_id = "1"
exercise_id = "2"

# Content that should fail the tests
fail_file = """public class Nimi {
    public static void main(String[] args) {

    }
}"""

# Content that should fail compiling
fail_compile_file = "tmc.py " + version + " was here"

# Content that should be successful in the tests
success_file = """public class Nimi {
    public static void main(String[] args) {
        System.out.println(\"tmc.py """ + version + """ was here\");
    }
}"""
