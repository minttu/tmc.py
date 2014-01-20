tmc.py
======

A python CLI for TestMyCode.

todo
====

	make it more user friendly
	handle changing directories better (currently you need to do everything in the same dir as tmc.py is)
	comment code
	--quiet
	--paste
	--request-review

usage
=====

	./tmc.py --auth                				# creates file with userdata for future connections
	./tmc.py --list                				# lists all courses
	./tmc.py --list --course n     				# lists all exercises from course that has the id of n
	./tmc.py --download --course n 				# downloads all exercises from course that has the id of n
	./tmc.py --submit --course n --exercise m 	# submits a exercise for testing
	./tmc.py --remove              				# removes all downloaded courses

installation
============

	get python2.7
	get pip
	pip install -r requirements.txt

license
=======

MIT, see `LICENSE`