make-folders:
	mkdir -p "./test/Campaigns/Bloomberg Businessweek+/Adfonic_BB"
	mkdir -p "./test/Campaigns/Bloomberg Businessweek+/Adfonic_BB_iPad"
	mkdir -p "./test/Campaigns/Bloomberg Businessweek+/Adfonic_BB_iPhone"
	mkdir -p "./test/Campaigns/Alien Family/Addmired/iPhone-iPod/iPod-iPhone Banners/320x53 iPod:iPhone (beneficial)/Static"
	mkdir -p "./test/Campaigns/*Retired Apps/Dream Park/Banners/480x32"
	mkdir -p "./test/Campaigns/*Retired Apps/Dream Park [test]/Banners/480x32"
	mkdir -p "./test/Campaigns/*Retired Apps/Dream Park {test}/Banners/480x32"
	mkdir -p "./test/Campaigns/*Retired Apps/Dream Park ;test;/Banners/480x32"
test: make-folders
	python box-file-renamer.py ./test
dry-run: make-folders
	python box-file-renamer.py --dryRun ./test
clean:
	rm -rf ./test
