import re
from pprint import pprint
import datetime


class Todo:
    todoCount = 0

    def __init__(self, rawLine):
        self.ID = Todo.todoCount
        self.priority = self.getPrio(rawLine)
        self.status = self.getStatus(rawLine)
        self.createDate = self.getCreateDate(rawLine)
        self.finishDate = self.getFinishDate(rawLine)
        self.dueDate = self.getDueDate(rawLine)
        self.description = self.getDescription(rawLine)
        self.contexts = self.getContexts(rawLine)
        self.projects = self.getProjects(rawLine)
        Todo.todoCount += 1


    def getPrio(self, rl):
        regex = r"\([A-Z]\)"
        try:
            return re.search(regex, rl).group()
        except Exception as e:
            #print("Prio not found: ", e, rl)
            pass #keine prio gesetzt. auch ok
    def getStatus(self,rl):
        regex = r"^x\s\d\d\d\d-\d\d-\d\d" #maybe the date is overkill, or stuff gets done without a done-date. revisit later. also in respect of the finish-date
        if re.search(regex, rl):
            return "done"
        else:
            return 'open'
    def getCreateDate(self, rl):
        #find a \d\d\d\d-\d\d-\d\d pattern without '^x\s' in front. oder von hinten aufrollen, nachdem das optional due: date übersprungen wurde
        regex_finishDate = r"(^x\s)(\d\d\d\d-\d\d\-\d\d)"
        regex_dueDate = r"due\:\d\d\d\d-\d\d-\d\d"
        rl = re.sub(regex_finishDate, "", rl)
        rl = re.sub(regex_dueDate,"",rl)
        regex = r"\d{4}-\d{2}-\d{2}"
        if re.search(regex, rl):
            return re.search(regex, rl).group()
        pass
    def getFinishDate(self,rl):
        regex = r"(^x\s)(\d\d\d\d-\d\d\-\d\d)"
        if re.search(regex, rl):
            try:
                return re.search(regex,rl).group(2)
            except Exception as e:
                print(e)
        else:
            pass
    def getDueDate(self, rl):
        regex = r"due\:\d\d\d\d-\d\d-\d\d"
        if re.search(regex, rl):
            dueDate_string = re.search(regex, rl).group()
            return dueDate_string.split(":")[1]
        else:
            return "          "
    def getDescription(self, rl):
        dates_regex = re.compile(r"\d\d\d\d-\d\d-\d\d")
        due_regex = re.compile(r"due\:")
        status_regex = re.compile(r"\([A-Z]\)")
        rl = re.sub(status_regex, "", rl)
        rl = re.sub(dates_regex,"",rl)
        rl = re.sub(due_regex,"",rl)
        return rl

    def getContexts(self, rl):
        regex = r"@[a-zA-Z]*"
        contexts = []
        if re.search(regex, rl):
            contexts = re.findall(regex, rl)
            #return re.search(regex, rl).group()
            return contexts
        else:
            pass
    def getProjects(self, rl):
        regex = r"\+[a-zA-Z]*"
        if re.search(regex, rl):
            return re.findall(regex, rl)
        else:
            pass

"""
with open("../../Lists/todo.txt", "r") as file:
    lines = file.readlines()
todo_list = []
for item in lines:
    try:
        newTodo = Todo(item)
        todo_list.append(newTodo)
        #pprint(vars(newTodo))
    except Exception as e:
        pass
#print("total number of tasks: %d" % Todo.todoCount)

def getByPrio(prio,status):
    print("\n\n\nlisting todos with prio ",prio, " and status ", status)
    print('\nID\tdue \t description')

    for x in todo_list:
        if x.priority == prio and x.status == status:
            print('-'*150)
            print(x.ID,"\t" ,x.dueDate,"\t" , x.description.strip())

def getByDueDate():
    print("\n\n\nlisting todos with some due date set")
    print('\nID\tdue \t description')
    for x in todo_list:
        if x.dueDate != "          ":
            print('-'*150)

            print(x.ID,"\t" ,x.dueDate.strip(),"\t" , x.description.strip())

def listAllContexts():
    context_list = []
    for todo in todo_list:
        if todo.contexts:
            for context in todo.contexts:
                context_list.append(context)
    context_list = set(context_list)
    context_list = sorted(list(context_list))
    print("\n\nall contexts, sorted alphabetically descending")
    for context in context_list:
        print(context)

def listByContext(context):
    result_list = []
    for todo in todo_list:
        try:
            if context in todo.contexts:
                print(todo.description)
        except:
            pass
"""
getByPrio('(A)','open')
listAllContexts()
listByContext("@UnifiedEngineering")
#getByDueDate()
