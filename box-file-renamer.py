#!/usr/bin/python

import sys
import os
import logging
import time
import argparse
import re

folderChangeCount = 0
fileChangeCount = 0
errorCount = 0
unsafeCharacters = '[\\":<>|*?!]'
fileList = []
subFolderList = []
rootDirectory = sys.argv[1]
###########################################################################
#Logging Setup
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

#Create console handler and set level to debug;
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

# Recursively walks the path at the given 'path' argument and returns a list of all files located therein
def listOfFiles(path):
	toReturn = []
	for root, subFolders, files in os.walk(path):
		for file in files:
			toReturn.append(os.path.join(root,file))
	return toReturn

# Recursively walks the path at the given 'path' argument and returns a list of all folders located therein
def listOfSubFolders(path):
	toReturn = []
	for root, subFolders, files in os.walk(path):
		for subFolder in subFolders:
			toReturn.append(os.path.join(root,subFolder))
	return toReturn

# Safely renames all the folders and subfolders of the given path, recursively.
def renameFolders(path): 
	for current in listOfSubFolders(path):
		if not isSafe(current):
			safeRename(current, 0)
			global folderChangeCount
			folderChangeCount += 1

# Safely renames all the files located at the given path, recursively.
def renameFiles(path): 
	for current in listOfFiles(path):
		if not isSafe(current):
			logger.debug('Renaming: "%(original)s"' % {"original" : current})
			safeRename(current, 0)
			global fileChangeCount
			fileChangeCount += 1

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
		os.rename(toRename, newName)
	except OSError as e:
		errorCount += 1
		logger.error("OS Error: An attempt to rename %(toRename)s failed. (Error %(errorNumber)s: %(errorText)s)" %
			{"errorNumber" : e.errno,
			"errorText" : e.strerror}
			)

# Performs check to safely rename a file or folder:
# - Unique Name: Checks to make sure that the new name isn't already in use by another file.
#	This could happen during mass renaming (e.g., 1:1.txt => 1-1.txt; 1|1.txt => 1-1.txt) and result in loss of data.
# 
# To accomplish this, the method calls recurses and tries adding the suffix ".CONFLICT-X", where X is the number of
# conflicts that existed because of identical file names.
def safeRename(toRename, attemptNumber):
	
	# Substitutes any unsafe characters with hyphens, a safe character for path names in Windows, Linux, and OS X.
	newName = re.sub(unsafeCharacters,"-", toRename)

	# If the attempt number is greater than zero, we'll need to start adding a conflict suffix.
	if attemptNumber > 0:
		newName = "%(newName)s.CONFLICT-%(attemptNumber)s" % {"newName" : newName, "attemptNumber" : attemptNumber}	
	# If the newName doesn't exist, we have a path name we can use.
	if not os.path.exists(newName):
		rename(toRename, newName)
		logger.debug('Renamed: "%(original)s" => "%(newName)s" after %(numberOfPreviousAttempts)s previous attempts.' %
			{"original" : toRename,
			"newName" : newName,
			"numberOfPreviousAttempts" : attemptNumber})
	# If the newName does exist, we'll need to try again.
	else:
		attemptNumber = attemptNumber + 1
		safeRename(toRename, attemptNumber)

###########################################################################
# Main Script
###########################################################################

logger.info("The script is starting.")

# First, we'll rename the folders.
renameFolders(rootDirectory)

# Now, we'll rename files.
renameFiles(rootDirectory)

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