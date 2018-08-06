import logging as log

class TableObj:
    def __init__(self):
        self.numOfCols = 0
        self.colHeaders = []
        self.content = []
        self.width = 0
        self.descriptionLimiter = 100

class Query:
    def __init__(self, queryList):
        self.urgency = self.setUrgency(queryList) #sets a LIST of urgencies, minimal len = 1
        self.priority = self.setPriority(queryList) # see above
        self.status = self.setStatus(queryList)
    def setUrgency(self,queryList):
        for item in queryList:
            if str(item).startswith("u="):
                item = item.replace("u=", "")
                try:
                    urgencyList = item.split(",")
                except:
                    urgencyList = item
            else:
                urgencyList = "0,1,2,3".split(",")
            return urgencyList

    def setPriority(self,queryList):
        for item in queryList:
            if item.startswith("p="):
                item = item.replace("p=", "")
                try:
                    priorityList = item.split(",")
                    priorityList = [p.replace(p,"".join(["(",p.upper(), ")"])) for p in priorityList]
                except:
                    priorityList = item
            else:
                priorityList = "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z".split(",")
                priorityList = [p.replace(p, "".join(["(", p.upper(), ")"])) for p in priorityList]
            return priorityList

    def setStatus(self,queryList):
        for item in queryList:
            if item.startswith("s="):
                print("setting distinct status")
                status = item.replace("s=","")
                if status == "o":
                    status = "open"
                elif status == "d":
                    status = "done"
            else:
                log.info("no status set")
                status = ["open","done"]
        return status

class Menu:
    def __init__(self):
        self.menuOptions = []

    def presentOptions(self):
        menuString = ""
        for option in self.menuOptions:
            menuString += "*   "+option[0]+"\n"
        menuString += "\n"
        choice = input(menuString)
        return choice

    def evaluate(self, choice):
        print("evaluating "+choice)
        validEntry = False
        for items in self.menuOptions:
            if choice == items[1]:
                validEntry = True
                function = getattr(self, items[2])
                function()
        if not validEntry:
            print("invalid Entry!\n")
            self.draw()


    def draw(self):
        choice = self.presentOptions()
        self.evaluate(choice)

    def function1(self):
        print("function1 chosen")
        self.draw()

    def function2(self):
        print("function2 chosen")
        self.draw()
    def function3(self):
        print("function3 chosen")
        self.draw()

class Config:
    def __init__(self):
        self.todotxt = ""
        self.infotxt = ""
        self.journaltxt = ""
        self.setpaths()

    def setpaths(self):
        with open("config/sources.txt","r") as source:
            lines = source.readlines()
            todoline = lines[0]
            self.todotxt = lines[0].split(":")[1].strip()
            self.infotxt = lines[2].split(":")[1].strip()
            self.journaltxt = lines[1].split(":")[1].strip()
