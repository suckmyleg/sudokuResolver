import time as time_

logs = {"START":[time_.time(), 0]}

from shutil import get_terminal_size
import numpy as np
import sys
import subprocess

#maxPaddingLeft = (get_terminal_size()[0] - 10)
decimals = 1
timeContent = 8
modulesNamesImported = []
modulesImported = []
mode = 0
modes = ["[{lt}] {first}{m}", "[{lt}] $HALF${first}{m} $HALF$", "[{lt}]$HALF$$HALF${first}{m}"]
lastSameLine = False


def startLog(name):
	global logs
	logs[name] = [time_.time(), 0]

def statusLog(name):
	global logs
	try:
		return time_.time() - logs[name][0]
	except:
		error("Error getting log from", name)
		return 0

def endLog(name):
	global logs
	try:
		if logs[name][1] == 0:
			logs[name][1] = time_.time()
		return logs[name][1] - logs[name][0]
	except:
		error("Error getting log from", name)
		return 0

def importModules(modulesList, finished=False):
	modules = [importModule(module) for module in modulesList]	
	if finished:
		fill("-")
		info("Finished importing!")
		fill("-")
	if len(modules) == 1:
		return modules[0]
	return tuple(modules)

def iM(data, finished=False):
	if type(data) == list:
		return importModules(data, finished=finished)
	else:
		return importModules([data], finished=finished)

def moduleKey(module):
	#print(modulesNamesImported)
	#print(modulesImported)
	if module in modulesNamesImported:
		return modulesNamesImported.index(module)
	else:
		modulesNamesImported.append(module)
		return len(modulesNamesImported)-1

def reuseModule(name):
	if name in modulesNamesImported:
		try:
			return modulesImported[moduleKey(name)]
		except:
			return False
	return False

def installModule(name):
	info("Installing module", name)
	try:
		subprocess.run(f"py -m pip install {name}", shell=True)
	except:
		pass

def importModule(name):
	moduleClone = reuseModule(name)
	if moduleClone:
		info(f"== ({moduleKey(name)}) Reusing {name}")
		return moduleClone

	info(f"=> ({moduleKey(name)}) Importing {name}")
	for loc in [name]:
		try:
			imp_new_module = type(sys)
			module = imp_new_module(loc)

			module.__dict__['info'] = info
			module.__dict__['warning'] = warning
			module.__dict__['error'] = error
			module.__dict__['log'] = log
			module.__dict__['iM'] = iM
			module.__dict__['sinceStart'] = sinceStart
			module.__dict__['fill'] = fill
			module.__dict__['importModules'] = importModules
			module.__dict__['importModule'] = importModule

			exec(open(name+".py").read(), module.__dict__)
		except:
			pass
		else:
			info(f"<= ({moduleKey(name)}) Imported {name}")
			modulesImported.append(module)
			return module

	try:
		module = __import__(name)
	except:
		pass
	else:
		info(f"<= ({moduleKey(name)}) Imported {name}")
		modulesImported.append(module)
		return module

	installModule(name)

	try:
		module = __import__(name)
	except:
		pass
	else:
		info(f"<= ({moduleKey(name)}) Imported {name}")
		modulesImported.append(module)
		return module

	modulesNamesImported.remove(name)
	error(f"No module: '{name}'")
	return None

def cleanTime(t):
	return int(t*10*decimals)/(10*decimals)

if decimals == 0:
	def cleanTime(t):
		return int(t)

def sinceStart():
	return cleanTime(statusLog("START"))

def time():
	return cleanTime(time_.time())

def displaylog(*messages, lt="Info", end="\n", flush=True, limit=True, sameLine=False):
	global lastSameLine
	maxPaddingLeft = (get_terminal_size()[0] - timeContent)
	FIRST = ""
	if len(messages) == 1 and type(messages[0]) == np.ndarray:
		FIRST = "{Matrix}\n"
		maxPaddingLeft = (get_terminal_size()[0]+8) * (len(messages)+1) + (get_terminal_size()[0] - timeContent)

	content = modes[mode].replace("{lt}", lt)
	content = content.replace("{first}", FIRST)
	content = content.replace("{m}", " ".join([str(m) for m in messages]))


	if limit:

		paddingLeft = (maxPaddingLeft-len(content) + (content.count("$HALF$")*6))
		if paddingLeft < 0:
			content = content.replace("$HALF$", "")
			if paddingLeft < -3:
				paddingLeft = -3
			content = content[0:maxPaddingLeft]
			#content = content[0:maxPaddingLeft+paddingLeft] + "."*(-paddingLeft)
			paddingLeft = 0
		else:
			content = content.replace("$HALF$", " "*(int(paddingLeft/2)))
		paddingLeft = (maxPaddingLeft-len(content) + (content.count("$HALF$")*6))

		if end == "\n":
			end = " "*paddingLeft + f"{sinceStart()}s"+end

	if sameLine:
		lastSameLine = True
		print("\r"+content, end=" "*paddingLeft + f"{sinceStart()}s", flush=False)
	else:
		if lastSameLine:
			lastSameLine = False
			print()
		print(content, end=end, flush=flush)

def fill(l):
	displaylog(l*get_terminal_size()[0], lt="")

def info(*messages, end="\n", flush=True, limit=True, sameLine=False):
	displaylog(*messages, lt="Info", end=end, flush=flush, limit=limit, sameLine=sameLine)

def log(*messages, end="\n", flush=True, limit=True, sameLine=False):
	displaylog(*messages, lt="Console", end=end, flush=flush, limit=limit, sameLine=sameLine)

def warning(*messages, end="\n", flush=True, limit=True, sameLine=False):
	displaylog(*messages, lt="Warning", end=end, flush=flush, limit=limit, sameLine=sameLine)

def error(*messages, end="\n", flush=True, limit=True, sameLine=False):
	displaylog(*messages, lt="Error", end=end, flush=flush, limit=limit, sameLine=sameLine)

def inp(*messages, end="", flush=False, limit=False, sameLine=False):
	displaylog(*messages, lt="Input", end=end, flush=flush, limit=limit, sameLine=sameLine)
	return input()