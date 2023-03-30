from logger import *
copy, json, random, pickle = iM(["copy", "json", "random", "pickle"], False)

toGiveI = 0
toGive = []#["6", "000000001000060020901000000710000005000000403000000700000000089000478000060000070", "1", ""]

inpP = inp
def inp(t):
	global toGiveI, toGive
	toGiveI += 1
	try:
		return toGive[toGiveI-1]
	except:
		return inpP(t)


board_to_resolve = [[0 for a in range(9)] for b in range(9)]
emptyFichas = [" ", 0, ""]
FICHAS = [a+1 for a in range(9)]
FICHAS_CURRENT = 0
tries = 0
lastTotalPosition = 89

hards = []
values = []
lastBar = ["", ""]
ai_data = False
last_ai_data = False

def learnFromFile(name):
	try:
		global ai_data
		if not ai_data:
			ai_data = get_ai_database_data()

		fill("/")
		info("$HALF$LOADING AI DATA FROM FILE")
		info("$HALF$fileName:", name)
		fill("/")
		
		try:
			info("Reading data from file")
			dataFromFile = pickle.loads(open(name, "rb").read())
			info("Readed data")
		except:
			fill("/")
			info("$HALF$FILE DOESNT EXISTS")
			info("$HALF$ABORTING")
			fill("/")
			return None
		
		loaded = 0

		info("$HALF$LOADING")
		for possible in range(len(dataFromFile)):
			for pos0 in range(len(dataFromFile[possible])):
				for pos1 in range(len(dataFromFile[pos0])):
					for board in dataFromFile[possible][pos0][pos1]:
						bb = getSudokuCode(board)
						if bb not in ai_data[possible][pos0][pos1]:
							ai_data[possible][pos0][pos1].append(bb)
							loaded += 1
							number = str(dataFromFile[possible][pos0][pos1].index(board))
							progress([pos0, pos1], bb, True, dec="#", 
								up=number, 
								down=number)

		save_ai_data(ai_data)
		info()
		fill("/")
		info("$HALF$FINISHED")
		info("$HALF$TOTAL LOADED")
		info(F"$HALF${loaded} BAD PATHS")
		fill("/")
	except Exception as e:
		fill("!")
		error("$HALF$Error loading ai data from file.")
		error("$HALF$Error code:")
		error(f"$HALF${e}")
		fill("!")

def getSudokuCode(board):
	code = ""
	for y in board:
		for x in y:
			code = f"{code}{x}"
	return code

def progress(position, code, sameLine = False, dec="=", up="\\", down="/"):
	global lastTotalPosition, lastBar
	totalPosition = position[1]*10 + position[0]
	movement = up
	if totalPosition < lastTotalPosition:
		#info(f"|{lastBar[1][0:len(lastBar[1])-4]}/{lastBar[0]}   |")
		movement = down
		if not position in hards:
			hards.append(position)
			values.append(1)
		else:
			values[hards.index(position)] = values[hards.index(position)]+1
	lastTotalPosition = totalPosition
	profression = int(((totalPosition)/(88))*100)
	bar = [' '*(100-profression), profression*dec+movement]
	#info(f"{start}|{bar[1]}{bar[0]}| try:{tries} {position} conflicts: {hards[values.index(max(values))]}({max(values)})", end=end, flush=flush)
	if tries % 20 == 0:
		info(f"|{code}|$HALF$$HALF$try:{tries} {position} conflicts: {hards[values.index(max(values))]}({max(values)})", sameLine=sameLine)
	lastBar = bar

def save_ai_data(data, force=False):
	global last_ai_data
	if force or ai_data != last_ai_data:
		info("Saving ai data")
		open("ai_data", "wb").write(pickle.dumps(data))
		info("Saved ai data")
		last_ai_data = copy.deepcopy(data)

def create_ai_database():
	info("Creating ai database")
	empty_data = [ [  [ [] for c in range(9)] for b in range(9)  ] for a in range(9) ]
	save_ai_data(empty_data, True)
	info("Created ai database")

def get_ai_database_data():
	global last_ai_data
	info("Loading ai data")
	startLog("getAiData")
	try:
		data = pickle.loads(open("ai_data", "rb").read())
	except:
		info("Ai data corrupt")
		create_ai_database()
		return get_ai_database_data()
	else:
		endLog("getAiData")
		info("Loaded ai data")
		last_ai_data = copy.deepcopy(data)
		return data

def get_board_x(board):
	return [[board[y][x] for y in range(9)] for x in range(9)]

def get_x_fichas(board, board_x, position):
	
	block_pos = [int((a)/3) for a in position]
	#print(position, block_pos)
	block = board[block_pos[1]*3][block_pos[0]*3:block_pos[0]*3+3] + board[block_pos[1]*3+1][block_pos[0]*3:block_pos[0]*3+3] + board[block_pos[1]*3+2][block_pos[0]*3:block_pos[0]*3+3]
	#print(position, block_pos, block)
	return board[position[1]] + board_x[position[0]] + block 

def get_possibles(board, board_x, position):
	possibles = []
	near = get_x_fichas(board, board_x, position)
	#print(near)
	for f in FICHAS:
		if not f in near:
			possibles.append(f)
	#print(possibles)
	return possibles






def valid_ficha(current_board, current_x_board, sudokuCode, pos, data=False):
	new_pos = [0,0]

	new_pos[0] = pos[0]
	new_pos[1] = pos[1]

	if pos[0] == 8:
		new_pos[0] = 0
		new_pos[1] += 1
	else:
		new_pos[0] += 1

	value = current_board[pos[1]][pos[0]]

	cb = copy.deepcopy(current_board)
	cxb = copy.deepcopy(current_x_board)

	cb[pos[1]][pos[0]] = 0
	cxb[pos[0]][pos[1]] = 0

	if value == 0:
		if pos == [8,8]:
			return current_board, current_x_board
		return valid_ficha(current_board, current_x_board, sudokuCode, new_pos, data)

	possibles = get_possibles(cb, cxb, pos)

	if value in possibles:
		if pos == [8,8]:
			return current_board, current_x_board
		return valid_ficha(current_board, current_x_board, sudokuCode, new_pos, data)

	return False, False

def resolve_ficha(board, board_x, sudokuCode, pos, data=False):
	global tries
	try:
		if not board[pos[1]][pos[0]] in emptyFichas:
			new_pos = [0,0]

			new_pos[0] = pos[0]
			new_pos[1] = pos[1]

			if pos[0] == 8:
				new_pos[0] = 0
				new_pos[1] += 1
			else:
				new_pos[0] += 1

			return resolve_ficha(board, board_x, sudokuCode,new_pos, data)
	except:
		return board, board_x

	current_board = copy.deepcopy(board)
	current_x_board = copy.deepcopy(board_x)

	possibles = get_possibles(current_board, current_x_board, pos)
	for value in possibles:
		progress(pos, sudokuCode, True)
		if tries >= 5000:
			#warning("Maximum tries done")
			return False, False
		try:
			current_board[pos[1]][pos[0]] = value
			current_x_board[pos[0]][pos[1]] = value

			sudokuCode = list(sudokuCode)
			sudokuCode[pos[0]+pos[1]*9] = str(value)
			sudokuCode = "".join(sudokuCode)

			#progress(pos, sudokuCode, True)

			if data == False or not sudokuCode in data[value-1][pos[0]][pos[1]]:
				#info(data[possibles[i]-1][pos[0]][pos[1]], limit=False)
				if pos == [8,8]:
					return current_board, current_x_board

				new_pos = [0,0]

				new_pos[0] = pos[0]
				new_pos[1] = pos[1]

				if pos[0] == 8:
					new_pos[0] = 0
					new_pos[1] += 1
				else:
					new_pos[0] += 1

				new_board, new_board_x = resolve_ficha(current_board, current_x_board, sudokuCode, new_pos, data)

				if new_board != False:
					return new_board, new_board_x

				if not data == False:
					data[value-1][pos[0]][pos[1]].append(sudokuCode)

				tries+=1
		except Exception as e:
			fill("!")
			error("$HALF$Error code:")
			error(f"$HALF${e}")
			fill("!")
			return False, False
	if tries == 0 and pos == [0,0]:
		warning("AI says that the sudoku cant be resolved")
	return False, False

def resolve_sudoku(b, ia=False, save_data=True, showBoard=True):
	if not b:
		return b
	board = copy.deepcopy(b)
	global ai_data, tries
	tries = 0
	board = commonBoard(board)
	#show_board(board)
	board_x = get_board_x(board)
	sudokuCode = getSudokuCode(board)

	bb, bb_x = valid_ficha(board, board_x, sudokuCode, [0,0], False)

	if not bb:
		info("Impossible to resolve")
		return None

	if ia:
		#startLog("resolveBoardAll")
		if not ai_data:
			ai_data = get_ai_database_data()
		#info("Resolving board")
		#startLog("resolveBoard")
		board, board_x = resolve_ficha(board, board_x, sudokuCode, [0,0], ai_data)
		#endLog("resolveBoard")
		#info("Done")
		if save_data:
			#startLog("saveAiData")
			save_ai_data(ai_data)
			#endLog("saveAiData")
		#endLog("resolveBoardAll")
		if not board and showBoard:
			info("Error trying to solve")
		else:
			if showBoard:
				show_board(board)
		#info(f"resolveBoard: {endLog('resolveBoard')} getAiData: {endLog('getAiData')} total: {endLog('resolveBoardAll')}", limit=False)
	else:
		#info("Resolving board")
		#startLog("resolveBoard")
		board, board_x = resolve_ficha(board, board_x, sudokuCode,[0,0])
		#endLog("resolveBoard")
		#info("Resolved")
		if not board and showBoard:
			info("Error trying to solve")
		else:
			if showBoard:
				show_board(board)
		#info(f"resolveBoard: {endLog('resolveBoard')}", limit=False)

	
def commonBoard(board):
	for i in range(len(board)):
		for j in range(len(board[i])):
			if board[i][j] in emptyFichas:
				board[i][j] = 0
	return board

def show_board(board):
	info("Code:", getSudokuCode(board))
	y = 0
	for height in board:
		line = ""
		i = 0
		for val in height:
			if val in ["", " ", 0]:
				val = " "
			s = ""
			if (i%3 == 0):
				s = "|"
			line = f"{line}{s}{val}"
			i += 1

		if (y%3 == 0 or y == 0):
			info("-"*len(line))
		y += 1
		info(f"{line}|")
	info("-"*len(line))

"""
100 010 001
010 010 010
001 010 100
000 111 000
111 111 111
000 111 000
001 010 100
010 010 010
100 010 001

100010001010010010001010100000111000111111111000111000001010100010010010100010001
"""
def generateRandomResolvableSudokuPatron(patron, limit):
	#info("Creating resolvable sudoku")
	for e in range(limit):
		board = [[0 for a in range(9)] for b in range(9)]
		for i in range(9):
			for j in range(9):
				if patron[i][j] == 1:
					board[i][j] = random.randint(1, 9)
		board_x = get_board_x(board)
		sudokuCode = getSudokuCode(board)

		bb, bb_x = valid_ficha(board, board_x, sudokuCode, [0,0], False)

		if not bb == False:
			return bb

	for e in range(limit):
		board_resolved = resolve_sudoku(generateRandomResolvableSudoku(5))
		board = [[0 for a in range(9)] for b in range(9)]
		for i in range(9):
			for j in range(9):
				if patron[i][j] == 1:
					board[i][j] = board_resolved[i][j]
		return bb

	return False

def sudokuCodeToBoard(sudokuCode):
	#info(sudokuCode)
	sudokuCode = sudokuCode + "0"*(81-len(sudokuCode))
	#info(sudokuCode)
	board = [[0 for a in range(9)] for b in range(9)]
	i = 0
	for y in range(9):
		for x in range(9):
			board[y][x] = int(sudokuCode[i])
			i+=1
	#info(board)
	return board

def generateRandomResolvableSudoku(n, limit=100):
	#info("Creating resolvable sudoku")
	for e in range(limit):
		board = [[0 for a in range(9)] for b in range(9)]
		for i in range(n):
			board[random.randint(0, 8)][random.randint(0, 8)] = random.randint(0, 9)
		board_x = get_board_x(board)
		sudokuCode = getSudokuCode(board)

		bb, bb_x = valid_ficha(board, board_x, sudokuCode, [0,0], False)

		if not bb == False:
			return bb
	return False


if __name__ == "__main__":
	fill(".")
	info("$HALF$Loading ai data")
	fill(".")
	ai_data = get_ai_database_data()

	while True:
		fill("-")
		info("$HALF$SUDOKU RESOLVER")
		info("1. Resolve random sudoku")
		info("2. Erase ai data")
		info("3. Load ai data")
		info("4. Train ai")
		info("5. Save ai data")
		info("6. Resolve sudoku")
		info("7. Create sudoku")
		info("8. Resolve sudoku patron")
		info("9. Train ai patron")
		fill("-")

		response = inp("Action: ")

		if response in ["7", "create"]:
			board = generateRandomResolvableSudoku(10)
			show_board(board)
			inp("Enter to see the solution:")
			resolve_sudoku(board, True, False)


		if response in ["6", "resolve"]:
			sudokuCode = inp("Sudoku(001443...): ")

			useAi = inp("Use Ai?").lower() in ["true", "si", "1", "usar", "y"]

			if useAi:
				fill("-")
				info("$HALF$IA$HALF$")
				fill("-")
				inp("Enter to start:")
			else:
				fill("-")
				info("$HALF$BRUTE FORCE$HALF$")
				fill("-")
				inp("Enter to start:")



			try:
				board_to_resolve = sudokuCodeToBoard(sudokuCode)
			except:
				warning("Sudoku code incorrect")
			else:
				resolve_sudoku(board_to_resolve, useAi, False)

		if response in ["5", "save"]:
			startLog("saveAiData")
			save_ai_data(ai_data)
			endLog("saveAiData")


		if response in ["9", "trainpatron"]:
			sudokuCode = inp("Sudoku(001001...): ")
			for e in range(int(inp("Trains: "))):
				try:
					board_to_resolve = generateRandomResolvableSudokuPatron(sudokuCodeToBoard(sudokuCode), limit=100)
				except:
					warning("Sudoku code incorrect")
				else:
					if board_to_resolve:
						show_board(board_to_resolve)
						resolve_sudoku(board_to_resolve, True, False)
					else:
						info("Try again")

		if response in ["8"]:
			sudokuCode = inp("Sudoku(001001...): ")
			try:
				board_to_resolve = generateRandomResolvableSudokuPatron(sudokuCodeToBoard(sudokuCode), limit=100)
			except:
				warning("Sudoku code incorrect")
			else:
				if board_to_resolve:
					show_board(board_to_resolve)
					resolve_sudoku(board_to_resolve, True, False)
				else:
					info("Try again")

		if response in ["4", "train"]:
			to_change = int(inp("Numbers to change: "))
			for e in range(int(inp("Trains: "))):
				resolve_sudoku(generateRandomResolvableSudoku(to_change), True, False, showBoard=False)

		if response in ["3", "load"]:
			learnFromFile(inp("fileName: "))

		if response in ["1", "resolverandom"]:
			useAi = inp("Use Ai?").lower() in ["true", "si", "1", "usar", "y"]

			if useAi:
				fill("-")
				info("$HALF$IA$HALF$")
				fill("-")
				inp("Enter to start:")
			else:
				fill("-")
				info("$HALF$BRUTE FORCE$HALF$")
				fill("-")
				inp("Enter to start:")

			resolve_sudoku(generateRandomResolvableSudoku(10), useAi, False)

		if response in ["2"]:
			if inp("This actin will remove all data. Confirm?(y/n)").lower() in ["true", "si", "1", "usar", "y"]:
				create_ai_database()
				ai_data = get_ai_database_data()
