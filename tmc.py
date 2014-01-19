#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests
import json
import sys
import getpass
import argparse
import os
import time
import dateutil.parser
import datetime
import pytz
import shutil

def vprint(level, message):
	if args is None:
		return
	if level is -1:
		sys.stderr.write(message+"\n")
	elif level <= args.verbose:
		sys.stdout.write(message+"\n")

def beautify(boolean):
	if boolean is True:
		return u"\033[32m✔\033[0m"
	else:
		return u"\033[31m✘\033[0m"

def handle_deadline(proper, message):
	if message is None:
		return "\033[32m                   Never!\033[0m"
	now = datetime.datetime.now(pytz.utc)
	then = dateutil.parser.parse(proper)
	if proper is None:
		return "\033[32m"+message+"\033[0m"
	if now < then:
		return "\033[32m"+message+"\033[0m"
	return "\033[31m"+message+"\033[0m"

class Config:
	def __init__(self):
		self.data = {}
		self.data["username"] = ""
		self.data["password"] = ""
		self.data["server"] = ""
		self.data["courses"] = []
		self.can_authenticate = False
		self.filename = args.filename
		self.fresh = False
		self.course_fresh = False

	def save(self):
		vprint(1, "Saving configuration for later use. ("+self.filename+")")
		try:
			with open(self.filename, "w") as fp:
				json.dump(self.data, fp)
				fp.close()
		except IOError:
			vprint(-1, "Saving failed")

	def load(self):
		if self.fresh:
			return
		try:
			with open(self.filename, "r") as fp:
				vprint(1, "Earlier configuration found.")
				self.data = json.load(fp)
				fp.close()
				self.test_auth()
				self.fresh = True
		except IOError:
			vprint(1, "No earlier cofiguration found.")
			self.create()
			self.test_auth()

	def create(self):
		vprint(0, "Creating new configuration.")
		self.data["server"] = raw_input("Server url [http://tmc.mooc.fi/mooc/]: ")
		if len(self.data["server"]) is 0:
			self.data["server"] = "http://tmc.mooc.fi/mooc/"
		self.data["username"] = raw_input("Username: ")
		self.data["password"] = getpass.getpass("Password: ")

	def get_auth(self):
		return (self.data["username"], self.data["password"])

	def get_url(self, slug):
		return self.data["server"] + slug

	def test_auth(self):
		r = requests.get(self.get_url("courses.json"), params={"api_version": 7}, auth=self.get_auth())
		if "error" in r.json():
			vprint(-1, "Authentication failed!")
			exit()
		else:
			vprint(-1, "Authentication was successfull!")
			self.can_authenticate = True
			self.save()

	def load_courses(self):
		if self.course_fresh:
			return
		self.load()
		r = requests.get(self.get_url("courses.json"), params={"api_version": 7}, auth=self.get_auth())
		self.data["courses"] = r.json()["courses"]
		self.save()
		self.course_fresh = True

	def get_course(self, id):
		self.load()
		self.load_courses()
		
		for i in self.data["courses"]:
			if i["id"] is id:
				return i
		return None

	def list_courses(self):
		self.load()
		self.load_courses()

		print "id, name"
		for i in self.data["courses"]:
			print str(i["id"]) + ", " + i["name"]

	def init_course(self, course):
		self.load()
		if course is None:
			vprint(-1, "Couldn\'t find that course by id ("+id+")")
			return
		try:
			os.mkdir(course["name"])
			vprint(0, "Created new directory for course ("+course["name"]+")")
		except OSError:
			pass

	def save_course(self, data):
		try:
			os.mkdir(data["course"]["name"])
		except OSError:
			pass
		try:
			with open(data["course"]["name"]+"/data.json", "w") as fp:
				json.dump(data, fp)
				fp.close()
		except IOError:
			vprint(-1, "Saving failed")

	def load_course(self, course):
		try:
			with open(course["name"]+"/data.json", "r") as fp:
				vprint(1, "Loading course.")
				data = json.load(fp)
				fp.close()
				return data
		except IOError:
			vprint(1, "Failed loading course.")
			return self.download_course(course)

	def download_course(self, course):
		self.load()
		if course is None:
			vprint(-1, "Couldn\'t find that course by id ("+str(course['id'])+")")
			return

		vprint(0, "Downloading course metadata.")
		r = requests.get(self.get_url("courses/"+str(course['id'])+".json"), params={"api_version": 7}, auth=self.get_auth())
		self.save_course(r.json())
		return r.json()

	def list_excercises(self, course):
		self.load()
		if course is None:
			vprint(-1, "Couldn\'t find that course by id ("+str(course['id'])+")")
			return
		data = self.load_course(course)

		# ugh
		tmparr = [	["r", "", ""],
					["e", "a", "c"],
					["t", "t", "o"],
					["u", "t", "m"],
					["r", "e", "p"],
					["n", "m", "l"],
					["a", "p", "e"],
					["b", "t", "t"],
					["l", "e", "e"]]
		for i in tmparr:
			print u"      │ %1s │ %1s │ %1s │" % (i[0], i[1], i[2])

		print u"%5s │ %1s │ %1s │ %1s │ %25s │ %s" % ("id", "e", "d", "d", "deadline", "name")
		print u"──────┼───┼───┼───┼───────────────────────────┼───────────────────"
		for i in data["course"]["exercises"]:
			print u"%5d │ %1s │ %1s │ %1s │ %25s │ %s" % (i["id"],
											beautify(i["returnable"]),
											beautify(i["attempted"]),
											beautify(i["completed"]),
											handle_deadline(i["deadline"], i["deadline_description"]),
											i["name"])

	def remove_everything(self):
		self.load()
		for i in self.data['courses']:
			try:
				shutil.rmtree(i['name'])
			except OSError:
				pass

def main():

	parser = argparse.ArgumentParser(description="Python CLI for TestMyCode.", prog="tmc.py")
	parser.add_argument("--verbose", "-v", dest="verbose", action="count")
	parser.add_argument("--version", "-V", action="version", version="%(prog)s v1")
	parser.add_argument("--config", "-C", dest="filename", action="store", default="tmc.json", help="alternative file to use for configuration")
	parser.add_argument("--auth", "-a", dest="command", action="store_const", const="auth", help="create authentication file")
	parser.add_argument("--list", "-l", dest="command", action="store_const", const="list", help="list all courses or exercises if --course is provided")
	parser.add_argument("--init", "-i", dest="command", action="store_const", const="init", help="initialize a folder for course id")
	parser.add_argument("--download", "-d", dest="command", action="store_const", const="download", help="downloads all exercises for course id")
	parser.add_argument("--remove", dest="command", action="store_const", const="remove", help="removes everything")
	parser.add_argument("--course", "-c", dest="course_id", action="store", type=int, help="course id")
	parser.add_argument("--exercise", "-e", dest="exercise_id", action="store", type=int, help="exercise id")
	global args
	args = parser.parse_args()
	if args.verbose is None:
		args.verbose = 0

	conf = Config()

	if args.command is None:
		args.command = "help"

	if args.command is "auth":
		conf.load()
	elif args.command is "list":
		if args.course_id is None:
			conf.list_courses()
		else:
			conf.list_excercises(conf.get_course(args.course_id))
	elif args.command is "init":
		if args.course_id is None:
			vprint(-1, "You need to provide a course id (--course) for this command!")
			return
		conf.init_course(conf.get_course(args.course_id))
	elif args.command is "download":
		if args.course_id is None:
			vprint(-1, "You need to provide a course id (--course) for this command!")
			return
		conf.download_course(conf.get_course(args.course_id))
	elif args.command is "remove":
		if args.course_id is not None:
			pass
		elif args.exercise_id is not None:
			pass
		else:
			sure = raw_input("This will remove everything this script created. ARE YOU SURE?! [N/y] ")
			if sure.upper() == "Y":
				conf.remove_everything()
	elif args.command is "help":
		parser.print_help()


if __name__ == "__main__":
	main()