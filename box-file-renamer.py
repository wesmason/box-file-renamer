#!/usr/bin/python

import sys
import os
import logging
import time
import argparse
import re

###########################################################################
# Global variables
###########################################################################

dryRun = False
errorCount = 0						# Number of errors for exit code and information.
fileChangeCount = 0					# Track the number of files that are renamed.
fileList = []						# The list of files
folderChangeCount = 0				# Track the number of folders that are renamed.
rootDirectory = ""					# The root directory whence the program recurses.
subFolderList = []					# The list of subfolders of the root directory.
unsafeCharacters = '[":<>|*?!]'	# The characters that are 'unsafe' and will be replaced with hyphens.

###########################################################################
# Logging Setup
###########################################################################

#If the logging folder doesn't exist, create it:
if not os.path.exists("./logs"):
	try:
		os.mkdir("./logs")
	except OSError:
		print "There was a problem creating the logging directory. Make sure that you have permission to write to the folder whence this script is executed."

#Create the logger
logger = logging.getLogger('box-file-renamer')
logger.setLevel(logging.DEBUG)

#Create console handler and set level to debug
ch = logging.FileHandler('logs/box-file-renamer_' + time.strftime("%Y-%m-%d_%H-%M-%S" + '.log', time.localtime()),
	mode='a',
	encoding=None,
	delay=False)
ch.setLevel(logging.DEBUG)

#Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#Add the formatter to the console handler
ch.setFormatter(formatter)
logger.addHandler(ch)

###########################################################################
# Helper Methods
###########################################################################

# Returns True if the file or folder has a safe name, and False if path has an unsafe name
def isSafe(path):
	#These are the unsafe characters, as explained by the Box Sync FAQ here:
	#https://support.box.com/entries/20364878-problems-syncing
	if re.search(unsafeCharacters, path):
		logger.debug('Unsafe characters detected: ' + path)
		return False
	return True

# Actually renames the given file or folder to the specified new name.
def rename(toRename, newName):
	# Attempt to actually rename the file now.
	try:
		if dryRun:
			logger.info("DRY RUN: Renaming %(toRename)s to %(newName)s" % {"toRename" : toRename, "newName" : newName})
		else:
			os.rename(toRename, newName)
	except OSError as e:
		global errorCount
		errorCount += 1
		logger.error("OS Error: An attempt to rename %(toRename)s failed. (Error %(errorNumber)s: %(errorText)s)" %
			{"toRename" : toRename,
			"errorNumber" : e.errno,
			"errorText" : e.strerror}
			)

# Safely renames all the files located at the given path, recursively.
def renameFiles(path): 
	for root, subFolders, files in os.walk(path, topdown=False):
		for thisFile in files:
			if not isSafe(thisFile):
				safeRename(thisFile, root, 0)
				global fileChangeCount
				fileChangeCount += 1

# Safely renames all the folders and subfolders of the given path, recursively.
def renameFolders(path): 
	for root, subFolders, files in os.walk(path, topdown=False):
		for subFolder in subFolders:
			if not isSafe(subFolder):
				safeRename(subFolder, root, 0)
				global folderChangeCount
				folderChangeCount += 1

# Performs check to safely rename a file or folder:
# - Unique Name: Checks to make sure that the new name isn't already in use by another file.
#	This could happen during mass renaming (e.g., 1:1.txt => 1-1.txt; 1|1.txt => 1-1.txt) and result in loss of data.
# 
# To accomplish this, the method calls recurses and tries adding the suffix ".CONFLICT-X", where X is the number of
# conflicts that existed because of identical file names.
def safeRename(toRename, parentFolder, attemptNumber):
	
	# Substitutes any unsafe characters with hyphens, a safe character for path names in Windows, Linux, and OS X.
	newName = re.sub(unsafeCharacters,"-", toRename)

	# If the attempt number is greater than zero, we'll need to start adding a conflict suffix.
	if attemptNumber > 0:
		newName = "%(newName)s.CONFLICT-%(attemptNumber)s" % {"newName" : newName, "attemptNumber" : attemptNumber}	
	# If the newName doesn't exist, we have a path name we can use.
	if not os.path.exists(newName):
		rename(os.path.join(parentFolder, toRename), os.path.join(parentFolder, newName))
		logger.debug('Renamed: "%(original)s" => "%(newName)s" after %(numberOfPreviousAttempts)s previous attempts.' %
			{"original" : toRename,
			"newName" : newName,
			"numberOfPreviousAttempts" : attemptNumber})
	# If the newName does exist, we'll need to try again.
	else:
		attemptNumber = attemptNumber + 1
		safeRename(toRename, parentFolder, attemptNumber)

###########################################################################
# Main Script
###########################################################################

def main():

	logger.info("The script is starting.")

	# Creates a parser for our arguments and options
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
		description='''Replaces unsafe characters in file and folder names before uploading files to Box.''',
		epilog='''For more information, please visit: https://github.com/wesmason/box-file-renamer\n(c) 2012 Wes Mason and Fiksu, Inc.''')

	# Adds arguments to our parser.
	#parser.add_argument('--loglevel', metavar="level", type=int, nargs=1, help="How verbose to be with logging. The default is none.")
	parser.add_argument('rootDirectory', metavar="rootDirectory", type=str, nargs=1, help="The directory through which the script should recurse.")
	parser.add_argument('--dryRun', dest='dryRun', action='store_true', help="Performs a dry run without making any changes.")
	
	# Prases the arguments
	args = parser.parse_args()

	global dryRun
	dryRun = args.dryRun

	# First, we'll rename the folders.
	renameFolders(args.rootDirectory[0])

	# Now, we'll rename files.
	#renameFiles(args.rootDirectory[0])

	global errorCount

	if errorCount > 0:
		logger.info("The script completed with %(numberOfErrors)s errors." % {"numberOfErrors" : errorCount})
		print "%(numberOfErrors)s errors occured. Please check the logs." % {"numberOfErrors" : errorCount}
		sys.exit(1)
	else:
		logger.info("The script completed with no errors. %(fileChangeCount)s file(s) changed. %(folderChangeCount)s folder(s) changed." %
		{"fileChangeCount" : fileChangeCount,
		"folderChangeCount" : folderChangeCount}
		)
		print("The script completed with no errors. %(fileChangeCount)s file(s) changed. %(folderChangeCount)s folder(s) changed." %
			{"fileChangeCount" : fileChangeCount,
			"folderChangeCount" : folderChangeCount}
			)
		sys.exit(0)
	
if __name__ == '__main__':
	main()