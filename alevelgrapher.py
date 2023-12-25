#Import Modules
import matplotlib.pyplot as plt
import numpy as np
import math
import copy


#FUNCTIONS

#Extracts numbers from input: Input can have delimiters such as ",", "|", space etc. 
#The period(".") cannot be a delimiter because it is used for representing floating point numbers.

def GetPoints(string:str) -> list:
    Done = False
    values = []
    tempstr = ''
    for char in string:
        if char.isnumeric() or char in ".-":
            Done = True
        else:
            Done = False
            values.append(tempstr)
            tempstr = ''
        if Done: tempstr += char
    else:
        values.append(tempstr)
    return [float(char) for char in values]

#Used in an input parsing process to find the intervals of where parentheses occur.
#Returns a list containing a bool to denote whether parantheses exist and the intervals from whence values ar inside the parantheses.

def BracketChecker(formula:str, index:int) -> list:
    if "(" and ")" in formula:
        Index1 = formula.find("(")
        Index2 = len(formula) - ''.join(list(reversed(formula))).find(")") - 1
        return [True, Index1, Index2]
    return [False,0,0]


def ValidateInput(prompt:str, valtype:str) -> any:
    Done = False
    while not Done:
        try:
            if valtype == "float": val = float(input(prompt))
            else: val = input(prompt)
            Done = True
        except:
            print("Your input was not valid, enter again")



    return val
    


#This function retrieves all the data that is needed to plot the graph from the user. 
#Returns a list containing the data.

def Parse_Input() -> list:
    Points1 = []
    Points2 = [None]
    CorrectCoords = False
    CorrectFormula = False
    for i in range(3):
        print("\n")
    print("Enter the names for your axes")
    Axis1 = ValidateInput("Enter name for X (independant variable) axis: ", "string")
    Axis2 = ValidateInput("Enter name for Y (dependant variable) axis: ", "string")
    Inputs = [Axis1, Axis2]
    print("Enter your points")
    while len(Points1) != len(Points2):
        if CorrectCoords:print("The number of X values should be the same as the number of Y values.")
        try:
            Points1 = GetPoints(input("Enter points for X axis: "))
            Points2 = GetPoints(input("Enter points for Y axis: "))
        except:
            print("Enter numbers")
        CorrectCoords = True

    Title = ValidateInput("Enter a Title for your graph: ", "string")
    while not CorrectFormula:
        try:
            Formula = ValidateInput("Enter your formula, use brackets properly for your formula to avoid ambiguity: ", "string")
            FormulaData = FindGradientandYintercept(Formula)
            CorrectFormula = True
        except:
            print("Your formula was not entered correctly, please re-enter your formula. Use y = m*x, if you want no formula.")
    UncertaintyY = ValidateInput("Enter your uncertainty for the y variable: ", "float")
    UncertaintyX = ValidateInput("Enter your uncertainty for the x variable: ", "float")
    FormulaData = FindGradientandYintercept(Formula)
    Inputs = [*Inputs, Points1, Points2, Title, *FormulaData, UncertaintyY, UncertaintyX]
    return Inputs

#Parses a formula given by the user
#Returns a list containing the operands of multiplication or division and the Y intercept
#The gradient will be either one of the two operands.

def FindGradientandYintercept(formula:str) -> list:
    ToIgnore = "+/*" + "="
    DecomposedFormula = [char for char in formula if char != " "]
    EqualsIndex = DecomposedFormula.index("=")
    NewFormula = "".join([DecomposedFormula[i] for i in range(EqualsIndex+1, len(DecomposedFormula))])
    YIntercept = ""
    OperandStr = ""
    MultiplicativeOperands = []
    InterceptArea1 = ""
    InterceptArea2 = ""
    OperandArea1 = ""
    OperandArea2 = ""
    Brackets1 = False
    Brackets2 = False
    Multiplication = False
    if "*" in NewFormula:
        MultiplicativeIndex = NewFormula.index("*")
        Multiplication = True
    elif "/" in NewFormula:
        MultiplicativeIndex = NewFormula.index("/")
    OperandArea1 = NewFormula[:MultiplicativeIndex]
    OperandArea2 = NewFormula[MultiplicativeIndex+1:]
    #Check for Brackets
    Brackets1 = BracketChecker(OperandArea1, MultiplicativeIndex)
    Brackets2 = BracketChecker(OperandArea2, MultiplicativeIndex)
    for i in range(1,len(OperandArea1)+1):
        if OperandArea1[MultiplicativeIndex-i] in ToIgnore and not (MultiplicativeIndex-i >= Brackets1[1] and MultiplicativeIndex-i <= Brackets1[2]): 
            InterceptArea1 = OperandArea1[:MultiplicativeIndex-i]
            break
        elif OperandArea1[MultiplicativeIndex-i] == "-" and not (MultiplicativeIndex-i >= Brackets1[1] and MultiplicativeIndex-i <= Brackets1[2]):
            if i == 1:
                InterceptArea1 = OperandArea1[:MultiplicativeIndex-i]
                break
            OperandStr += "-"
            InterceptArea1 = OperandArea1[:MultiplicativeIndex-i]
            break
        OperandStr += OperandArea1[MultiplicativeIndex-i]
    OperandStr = ''.join(list(reversed(OperandStr)))
    MultiplicativeOperands.append(OperandStr)
    OperandStr = ""

    for i in range(len(OperandArea2)):
        if OperandArea2[i] in ToIgnore and not (i >= Brackets2[1] and i <= Brackets2[2]):
            InterceptArea2 = OperandArea2[i+1:]
            break
        elif OperandArea2[i] == "-":
            if i!=0 and not (i >= Brackets2[1] and i <= Brackets2[2]):
                InterceptArea2 = OperandArea2[i:]
                break
        OperandStr += OperandArea2[i]
    MultiplicativeOperands.append(OperandStr)
    if any(InterceptArea1) and any(InterceptArea2):
        YIntercept = InterceptArea1 + " + " + InterceptArea2
    elif any(InterceptArea1):
        YIntercept = InterceptArea1
    else:
        YIntercept = InterceptArea2

    if not Multiplication:
        MultiplicativeOperands[0] = f"1/{MultiplicativeOperands[0]}"
    if not any(YIntercept):
        YIntercept = "NULL"
    for index,operand in enumerate(MultiplicativeOperands):
        if not any(operand):
            MultiplicativeOperands[index] = "NULL"
    
    return [MultiplicativeOperands, YIntercept]

#Performs linear regression on a set of x values and y values 
#Returns a list containing the gradient, the y intercept, the actual function as a lambda and R squared.

def LinearRegression(xpoints:list, ypoints:list) -> list:
    XMean = sum(xpoints)/len(xpoints)
    YMean = sum(ypoints)/len(ypoints)
    XDistance = [xpoint-XMean for xpoint in xpoints]
    YDistance = [ypoint-YMean for ypoint in ypoints]
    XDistanceSquared = [xpoint**2 for xpoint in XDistance]
    Gradient = round(sum([XDistance[i]*YDistance[i] for i in range(len(XDistance))])/sum(XDistanceSquared),3)
    YIntercept = round(YMean - XMean*Gradient,3)
    SubLambda = lambda x: x*Gradient + YIntercept
    YValues = [SubLambda(x) for x in xpoints]
    YValDist = [YVal - YMean for YVal in YValues]
    RSquared = round(sum([yvalest**2 for yvalest in YValDist])/sum([yvalact**2 for yvalact in YDistance]),3) * 100
    return [Gradient, YIntercept, RSquared, SubLambda, YValues]

#Returns a y = x plot with respect to our x values so that the graph is relative to y = x

def RetrieveBasePlot(Points1:list,Points2:list) -> list:
    BasePlot = []
    if Points1[-1] >= Points2[-1]:
        BasePlot = [x for x in range(math.ceil(Points1[-1])+1)]
    else:
        BasePlot = [x for x in range(math.ceil(Points2[-1])+1)]
    return BasePlot

#This procedure prints important data from the graphing and regression
#Prints, the gradients, the y intercepts and the accuracy of the regression

def PrintData(Data:list, LinearData:list) -> None:
    for i in range(2):print("\n")
    print(f"Your Y intercept: {Data[6]} is equal to {LinearData[0][1]}")
    print(f"Your gradient: {LinearData[0][0]} and is equal to either {Data[5][0]} or {Data[5][1]} depending on which measurement is on your x axis")
    print(f"The two gradients of the other lines are: {LinearData[1][0]} and {LinearData[2][0]}")
    print(f"The two y intercepts of the other lines are: {LinearData[1][1]} and {LinearData[2][1]}")
    print(f"Your line of best fit is {LinearData[0][2]}% accurate with respect to your actual values")
    for i in range(2):print("\n")

#Adds the uncertainties to the y values, depending on the mode it either adds or subtracts the uncertainty
#Returns a list with the added uncertainties

def AddUncertainty(ypoints:list,Uncertainty:float, mode:bool) -> list:
    midpoint = len(ypoints)//2
    for i in range(midpoint):
        if mode:ypoints[i] += Uncertainty
        else:ypoints[i] -= Uncertainty
    for i in range(midpoint, len(ypoints)):
        if mode:ypoints[i] -= Uncertainty
        else:ypoints[i] += Uncertainty
    return ypoints

#Performs linear regression and plots it onto the canvas with error bars (only for the first series(line of best fit without uncertainties))
#Returns a list containing the linear regression data for that line.

def RegressAndPlot(xpoints:list, ypoints:list, Uncertainty:float, UncertaintyX:float, mode:bool) -> list:
    LineData = LinearRegression(xpoints, ypoints)
    PlottingY = [LineData[3](x) for x in [0,*xpoints]]
    plt.plot([0,*xpoints], PlottingY)
    if mode:
        DrawErrorBars(xpoints, LineData[4], Uncertainty, True)
        DrawErrorBars(xpoints, LineData[4], UncertaintyX, False)
    return LineData

#Draws the error bars on the canvas, draws either horizontal or vertical error bars depending on the mode.

def DrawErrorBars(xpoints:list, ypoints:list, Uncertainty:float, mode:bool) -> None:
    for i,v in enumerate(xpoints):
        if mode:
            plt.plot([v,v], [ypoints[i]-Uncertainty, ypoints[i]+Uncertainty], color = "black")
        else:
            plt.plot([v-Uncertainty, v+Uncertainty], [ypoints[i],ypoints[i]], color = "red")

#Taking the input from the user then storing it
Data = Parse_Input()
Uncertainty = Data[7]
UncertaintyX = Data[8]
xpoints = np.array(Data[2])
ypoints = np.array(Data[3])

#Perform linear regression then plot. Also plots the baseplot so the graph is relative to y = x
#Also plots the x and y values by themselves to show the points without the linear regression, they are connected with a dashed line.

BasePlot = RetrieveBasePlot(xpoints, ypoints)
plt.plot(BasePlot, BasePlot, linewidth = 0)
plt.scatter(xpoints,ypoints)
plt.plot(xpoints,ypoints, linestyle = "dashed")
LinearData = RegressAndPlot(xpoints,ypoints, Uncertainty, UncertaintyX, True)
LinearData2 = RegressAndPlot(xpoints,AddUncertainty(copy.deepcopy(ypoints), Uncertainty, True), Uncertainty, Uncertainty, False)
LinearData3 = RegressAndPlot(xpoints, AddUncertainty(copy.deepcopy(ypoints), Uncertainty, False), Uncertainty, UncertaintyX, False)
LinearDataPackage = [LinearData, LinearData3, LinearData2]

#Print the data to the user and perform any any accessory visual changes to the canvas. 
#Also invokes the function that actually shows the function

PrintData(Data, LinearDataPackage)
plt.xlabel(Data[0])
plt.ylabel(Data[1])
plt.title(Data[4], loc = 'center')
plt.grid()
plt.show()