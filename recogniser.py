from logger import *
cv2, json, np, mss, PIL, copy = iM(["cv2", "json", "numpy", "mss", "PIL", "copy"])
import matplotlib.pyplot as plt

bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
#bounding_box = {'top': 100, 'left': 0, 'width': 400, 'height': 400}

AREAMIN = (bounding_box["width"]*bounding_box["height"])/10000
AREAMIN = 1000

#info(AREAMIN)

sct = mss.mss()


try:
	numbersData = json.loads(open("numbersData", "r").read())
except:
	numbersData = [[] for e in range(10)]

#https://www.educative.io/answers/how-to-convert-hex-to-rgb-and-rgb-to-hex-in-python
def rgb_to_hex(r, g, b):
	return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def display_group(group):
	for g in group:
		info(g, limit=False)


def indiceCodeToNumberGeneral(indicesCode):
	indices = []
	for number in range(10):
		if len(numbersData[number]) > 0:
			indices.append( ( len(list(filter(lambda x: (x == indicesCode), numbersData[number])))*100 ) / len(numbersData[number]) )
		else:
			indices.append(0)

	highest = sorted(indices)[::-1]
	info(indices, limit=False)

	if highest[0] == 0:
		return False

	#info(numbersData)
	return indices.index(highest[0])

def indiceCodeToNumber(indicesCode, autoLearn=True):
	cells = indicesCode.split(":")
	nCells = len(cells)

	indices = []
	for number in range(10):
		leng = len(numbersData[number])
		if leng > 0:
			indice = 0
			for code in numbersData[number]:
				goods = 0

				splittedCode = code.split(":")
				try:
					for cellN in range(nCells):
						if cells[cellN] == splittedCode[cellN]:
							goods += 1
				except:
					pass

				indice += goods/nCells
			indices.append( ( indice*100 ) / leng )
		else:
			indices.append(0)

	highest = sorted(indices)[::-1]
	info([(int(a*100)/100) for a in indices], limit=False)
	# 3 4 9
	if highest[0] == 0:
		return False
	else:
		if autoLearn and highest[0] > 65 and len(numbersData[indices.index(highest[0])]) > 600:
			info("AutoLearning")
			saveIndiceCodeToNumber(indicesCode, indices.index(highest[0])) 

	#info(numbersData)
	return indices.index(highest[0])

def saveIndiceCodeToNumber(indicesCode, number):
	if not indicesCode in numbersData[number]:
		numbersData[number].append(indicesCode)
		open("numbersData", "w").write(json.dumps(numbersData))


def getNumber(horizontalImage, columnas=10, filas=10, filaWidth=10, columnHeight=10):
	horizontalImage = cv2.resize(horizontalImage, dsize=(filaWidth*filas, columnHeight*columnas), interpolation=cv2.INTER_CUBIC)

	totalHeight = columnHeight*columnas
	totalWidth = filaWidth*filas

	height = int(totalHeight/filas)
	#info(columnas)
	width = int(totalWidth/columnas)

	area = height*width

	indices = []
	indicesCode = ""

	backgroundColor = False
	fontColor = False

	for i in range(columnas):
		for j in range(filas):
			fromX = width*i
			toX = width*(i+1)

			fromY = height*j
			toY = height*(j+1)

			colors = []
			counts = []

			totalColors = 0

			for y in range(height):
				for x in range(width):
					color = int(horizontalImage[y+fromY][fromX+x]/10)
					#info(color)
					if not color in colors:
						if (not backgroundColor or (color == backgroundColor or color == fontColor)):
							totalColors+=1
							colors.append(color)
							counts.append(1)
					else:
						counts[colors.index(color)] += 1


			most = []

			for c in range(totalColors):
				index = int((counts[c]*100)/area)
				most.append([colors[c], index])
				if index > 30:
					color = str(colors[c])
					if color == "25":
						color = ""
					if c != 0:
						color = "-"+color
					indicesCode += f"{color}_{str(index)[0]}"

			if j != filas:
				indicesCode += f":"
			indices.append(most)



	number = indiceCodeToNumberGeneral(indicesCode)

	if not number:
		pass
		#number = indiceCodeToNumber(indicesCode)

	if not number and False:
		try:
			number = 0#int(" ")
			#number = int(input("Number: "))
			saveIndiceCodeToNumber(indicesCode, number)
		except:
			pass

		

	#info(number, indicesCode, limit=False)
	info(number)
	return number



def groupHorientation(npImage, h=0):

	"""
	h indicates where is the y
	h = 1
		
	realImage(Horizontal)
	vv1 111
	vv1 000
	vv1 000
	vv1 000
		vv2

	##Vertical##

	vv1 0001
	vv1 0001
	vv1 0001
		vv2

	x = [vv2, vv1][h]
	del [vv2, vv1][h]
	y = [vv2]

	group[1][h] = [x, y][h]
	[x, y]


	##Horizontal##

	h = 0
	vv1 111
	vv1 000
	vv1 000
	vv1 000
		vv2
	x = [vv2, vv1][h]
	del [vv2, vv1][h]
	y = [vv1]

	group[1][h] = [x, y][h]
	[x, y]


	"""
	groups = []

	group = False
	for vv1 in range(len(npImage)):
		dates = npImage[vv1]

		last = None
		
		#Por valor dentro de la columna (y)
		for vv2 in range(len(dates)):
			v = dates[vv2]

			datesP = [vv2, vv1]

			#Si el ultimo valor no es el de ahora, se crea un nuevo grupo_vector
			if last != v:
				if group and (group[0][1][h] - group[0][0][h]) >= AREAMIN:
					#print((group[1][h] - group[0][h]))
					groups.append(group)

				x = datesP[h]
				del datesP[h]
				y = datesP[0]
				group = [[[x, y], [x, y]], v]
				last = v
			else:
				#info("Expanding vector_group", group)
				group[0][1][h] = datesP[::-1][h]
				#info("Ed vector_group", group)
	return groups







def areaDeCuadrado(c):
	return abs(c[0][1][0] - c[0][0][0]) * abs(c[0][2][1] - c[0][1][1])

def group(image_vertical, image_horizontal):
	info("Searching vertical_groups")
	vertical_groups = groupHorientation(image_vertical, 1)

	info("Searching horizontal_groups")
	horizontal_groups = groupHorientation(image_horizontal, 0)

	#display_group(vertical_groups)

	info("Searching squares")

	cuadrados = []

	i = 0
	for v in horizontal_groups:
		cuadrado = searchGeometry(v, [vertical_groups, horizontal_groups[i:]], geometry=[])
		#print(cuadrado)
		if not cuadrado == False:
			area = areaDeCuadrado(cuadrado)
			if area > 50:
				cuadrados.append([cuadrado, area])
				#print(cuadrado, area)
		i+=1
	info("Done")

	return cuadrados

def searchGeometry(v, groups, geometry=[], maxn=4):
	geometry.append(v)
	geometrySize = len(geometry)
	turn = (geometrySize+1)%2

	#info(geometry, limit=False)

	for a in groups[turn]:
		#info(len(geometry))
		toCheck = [v[0], a[0]]

		#info()
		#info(turn, toCheck)
		if turn:
			toCheck = toCheck[::-1]
		#info(turn, toCheck)
		#if turn:
		#	input()
		if ((a[1] == v[1]) and intersects_2_groups(toCheck[0], toCheck[1])) and not list(filter(lambda x: (x is a), geometry)):# and ((len(geometry)+1) != maxn or intersects_2_groups(a, geometry[0])):
			#print(geometrySize, turn, toCheck[0], toCheck[1])
			
			
			#print(v)



			if maxn == geometrySize:
				#info("END")
				#info(geometrySize)
				if intersects_2_groups(geometry[0][0], a[0]):
					ac = copy.deepcopy(a)
					ac[0][1][turn] = v[0][1][turn]
					#info("data", geometry, geometry[0][0], limit=False)
					return [[end[0][0] for end in geometry], ac[1]]
			else:
				#info("CONTINUE")
				ac = copy.deepcopy(a)
				ac[0][1][turn] = v[0][1][turn]
				b = searchGeometry(ac, groups, geometry=geometry, maxn=maxn)
				if not b == False:
					#info("RETURNING")
					#info(geometrySize)
					return b

				del geometry[-1]
	return False


def intersects_2_groups(v1, v2):
	#v1 beetween v2 x, v2 beetween v2 x, v1 beetween v2 y, v2 beetween v1 y
	#info(v1, v2)





	"""	
	h - v 0
	v - h 1
	h - v 0
	v - h 1


	v1[0]    v2[0]
	----------|- v1[1]
	          |
	          |
	          |
			v2[1]

			v2[0] == v1[1]

			v1 same y [1]
			v2 same x [0]
	"""
	"""if True in [ v2[1][1] >= v1[0][1] >= v2[0][1] and v1[1][0] >= v2[0][0] >= v1[0][0],  v1[1][1] >= v2[0][1] >= v1[0][1] and v2[1][0] >= v1[0][0] >= v2[0][0] ]:
		info(( v2[1][1] >= v1[0][1] >= v2[0][1] and v1[1][0] >= v2[0][0] >= v1[0][0] ), ( v1[1][1] >= v2[0][1] >= v1[0][1] and v2[1][0] >= v1[0][0] >= v2[0][0] ))
	"""
	return v1[1][0] >= v2[0][0] >= v1[0][0] or v2[1][1] >= v1[1][1] >= v2[0][1]

def get_vertical_image(image_horizontal):
	return np.rot90(image_horizontal)

def screenImage():
	return sct.grab(bounding_box)

def screen():
	return np.array(screenImage())

def detectSudoku():
	numpy_image = screen()

	resized = cv2.resize(numpy_image, dsize=(int(bounding_box["width"]/2), int(bounding_box["height"]/2)), interpolation=cv2.INTER_CUBIC)

	image_horizontal = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

	image_vertical = get_vertical_image(image_horizontal)

	fill("--")

	#getNumber(image_horizontal)

	squaresGrouped = {}

	squares = group(image_vertical, image_horizontal)

	for g in squares:
		#print(g)
		gg = g[0][0]
		info(gg, limit=False)#, (g[0][0], g[0][1]),(g[1][1], g[2][1]))
		cv2.line(resized,(gg[0][0], gg[0][1]),(gg[1][0], gg[1][1]),(255,0,0),5)
		cv2.line(resized,(gg[1][0], gg[1][1]),(gg[2][0], gg[2][1]),(255,0,0),5)
		cv2.line(resized,(gg[2][0], gg[2][1]),(gg[3][0], gg[3][1]),(255,0,0),5)
		cv2.line(resized,(gg[3][0], gg[3][1]),(gg[0][0], gg[0][1]),(255,0,0),5)
		try:
			squaresGrouped[str(g[1])] += 1
		except:
			squaresGrouped[str(g[1])] = 1

	for area in squaresGrouped.keys():
		print(squaresGrouped[area], "of area", area)


	if True:
		cv2.imshow('screen', resized)
		if (cv2.waitKey(1) & 0xFF) == ord('q'):
			cv2.destroyAllWindows()

if __name__ == "__main__":
	while True:
		detectSudoku()
		AREAMIN = 100