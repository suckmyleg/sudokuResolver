from logger import *
recogniser = iM(["recogniser"])
mode = 0


if mode:
	while True:
		startLog("detectSudoku")
		recogniser.detectSudoku()

		recogniser.AREAMIN=(recogniser.AREAMIN*endLog("detectSudoku"))/0.4
		info(endLog("detectSudoku"), recogniser.AREAMIN)

else:
	while True:
		startLog("detectSudoku")
		for e in range(2):
			recogniser.detectSudoku()
			info(statusLog("detectSudoku")/(e+1), recogniser.AREAMIN)
		recogniser.AREAMIN=(recogniser.AREAMIN*(endLog("detectSudoku")/(2)))/0.4