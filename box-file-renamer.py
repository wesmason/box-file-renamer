#!/usr/bin/python

import sys
import os
import logging
import time
import argparse
import re

unsafeCharacters = '[\\":<>|*?]'
fileList = []
subFolderList = []
rootDirectory = sys.argv[1]
###########################################################################
#Logging Setup
###########################################################################

#If the logging folder doesn't exist, create it:
if not os.path.exists("./logs"):
	os.mkdir("./logs")

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
# Main Script
###########################################################################

# Returns the current list of files in the folder, recursively.
def listOfFiles(path):
	toReturn = []
	for root, subFolders, files in os.walk(path):
		for file in files:
			toReturn.append(os.path.join(root,file))
	return toReturn

# Generate a list of all the files in the root directory, recursively.
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
			safeRename(current)
# Safely renames all the files located at the given path, recursively.
def renameFiles(path): 
	for current in listOfFiles(path):
		if not isSafe(current):
			safeRename(current)

# Returns True if the file or folder has a safe name.
def isSafe(path):
	#These are the unsafe characters, as explained by the Box Sync FAQ here:
	#https://support.box.com/entries/20364878-problems-syncing
	if re.search(unsafeCharacters, path):
		logger.debug('Unsafe characters detected: ' + path)
		return False
	return True

# Safely renames the file or folder at the given path.
def safeRename(toRename):
	logger.debug('Renaming: "%(original)s"' % {"original" : toRename}) 
	renamed = re.sub(unsafeCharacters,"-", toRename)
	logger.debug('Renamed: "%(original)s" => "%(renamed)s"' % {"original" : toRename, "renamed" : renamed}) 

# First, we need to rename folders.
renameFolders(rootDirectory)

# Now, we can rename files.
renameFiles(rootDirectory)
