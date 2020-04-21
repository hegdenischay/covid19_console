import json
import os
import sys

state = ""
dist = ""

def justIn():
	print("Looks like you are new to this program. Please input your State and District data")
	global state 
	state = input()
	global dist
	dist = input()
	os.chdir("/tmp/")
	try:
		os.makedirs("pycovid")
	except:
		os.system("rm -rf /tmp/pycovid/")
		os.chdir("/tmp")
		os.makedirs("pycovid")
	os.chdir("/tmp/pycovid/")
	required_data = {"State": state, "District": dist}
	fp = open("config.json",'w')
	json.dump(required_data,fp)
	fp.close()

def addAgain():
	print("Looks like something went wrong with what you typed. Here are possible reasons:\n1. Keep spaces between state names.\n2. Please check if your locality is in the json files for local stats.")
	os.system('rm -rf /tmp/pycovid')
	print("Please enter your State and District again")
	global state 
	state = input()
	global dist
	dist = input()
	print(state, dist)
	required_data = {"State": state, "District": dist}
	os.chdir("/tmp/")
	os.makedirs("pycovid")
	os.chdir("/tmp/pycovid/")
	fp = open("config.json",'w')
	json.dump(required_data,fp)
	fp.close()

def getStats(jsonFile, state, dist):
    # try to open the json file, or download
	try:
		fp = open(jsonFile,'rb')
	except:
		if jsonFile == "state_district_wise.json":
			os.system('wget --quiet https://api.covid19india.org/state_district_wise.json' )
		elif jsonFile == "latest":
			os.system('wget -O latest --quiet https://api.rootnet.in/covid19-in/stats/latest')
		fp = open(jsonFile, 'rb')

	local = json.loads(fp.read())
	# delet old json files
	try:
		local['lastRefreshed'][:8] == (os.popen('date +%Y-%m-%d').readlines()[0].strip())
	except:
		fp.close()
		try:
			os.system('rm '+jsonFile)
		except:
			pass
		os.system('wget --quiet https://api.covid19india.org/state_district_wise.json')
		os.system('wget -O latest --quiet https://api.rootnet.in/covid19-in/stats/latest')
		local = json.loads(open(jsonFile,'rb').read())
	
	# save downloaded file for offline access 

		if jsonFile == "state_district_wise.json":
			curr_date = os.popen('date +%Y-%m-%d').readlines()[0].strip()
			local['lastRefreshed'] = curr_date
			os.system('rm ' + jsonFile)
			fp = open(jsonFile, 'w')
			json.dump(local,fp)
			fp.close()

	if jsonFile == 'state_district_wise.json':
		active = "NA"
		try:
			confirmed = local[state]['districtData'][dist]['confirmed']
		except:
			addAgain()
			print("Please run the program again.")
			sys.exit(0)
		deceased = "NA"

	if jsonFile == 'latest':
		key = 0
		for i in range(33):
			if local['data']['regional'][i]['loc'] == state:
				key = i
		# api seems to think "Telangana" is spelled "Telengana"
		if state == "Telangana":
			key = 28
		try:
			confirmed  = local['data']['regional'][i]['totalConfirmed']
			active = confirmed - local['data']['regional'][i]['discharged']
			deceased = local['data']['regional'][i]['deaths']
		except:
			addAgain()
			print("Please run the program again")
			sys.exit(0)
	
	if jsonFile == 'latest' and state == "NA":
		confirmed = local['data']['summary']['total']
		active = confirmed - local['data']['summary']['discharged']
		deceased = local['data']['summary']['deaths']

	return active, confirmed, deceased

#get the local casefile from https://api.covid19india.org/state_district_wise.json

def main():

	# Country and State data from https://api.rootnet.in/
	try:
		os.chdir("/tmp/pycovid/")
		configs = json.loads(open("config.json",'rb').read())
	except:
		justIn()
		configs = json.loads(open("config.json",'rb').read())

	global state
	state  = configs['State']
	global dist
	dist = configs['District']

	print("Coronavirus Statistics".center(80, '-'))
	active, confirmed, deceased = getStats('latest', "NA", "NA")
	print("Country Stats: ".ljust(20) + ("Confirmed: " + str(confirmed)).ljust(20) + (" Active: " + str(active)).ljust(20) + (" Deceased: " + str(deceased)).ljust(20) )
	active, confirmed, deceased = getStats('latest', state, 'NA')
	print("State Stats: ".ljust(20) + ("Confirmed: " + str(confirmed)).ljust(20) + (" Active: " + str(active)).ljust(20) + (" Deceased: " + str(deceased)).ljust(20) )
	active, confirmed, deceased = getStats('state_district_wise.json', state, dist)
	print("Local Stats: ".ljust(20) + ("Confirmed: " + str(confirmed)).ljust(20) + (" Active: " + str(active)).ljust(20) + (" Deceased: " + str(deceased)).ljust(20) )

if __name__ == "__main__":
	main()
