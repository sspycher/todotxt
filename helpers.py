import datetime
import logging as log
import Todo
import tdt
import Classes
import tableoutput as table
from operator import itemgetter, attrgetter, methodcaller

config = Classes.Config()

# wrapping input to use mock.patch in unittest as suggested by
# https://stackoverflow.com/questions/21046717/python-mocking-raw-input-in-unittests
def get_input(prompt):
    return input(prompt)

def export_CSV(result):
    log.info("asking if user wants to export")
    export = input("do you want to export this? y/n\n")
    # -------------------------------------------------------------------------------------------#
    if export == 'n':
        log.info("no export. cancelling")
        pass
    # -------------------------------------------------------------------------------------------#
    elif export == 'y':
        log.info("exporting connected list")
        table.exportThis(result)
    else:
        print("invalid entry")

def addTodo_CollectContent():
    global config
    newTodoPrio = "(" + get_input('a-z\n').upper() + ")"
    # todo: add regex based verification
    newTodoText = input('add your todo text\n')
    newTodoUrgency = "{" + input('0-3\n') + "}"
    # todo: add regex based verification
    newTodoSize = "$$" + input('xs-xxl\n').upper()
    newTodoCreateDate = datetime.datetime.now().strftime("%Y-%m-%d")
    newTodoDueDate = input('<YYYY-MM-DD>\n')
    if len(newTodoDueDate) > 0:
        newTodoDueDate = "due:" + newTodoDueDate
    rawline = " ".join([newTodoPrio, newTodoCreateDate, newTodoText, newTodoUrgency, newTodoSize, newTodoDueDate])
    return rawline

def addTodo(todo_list):
    global config
    log.debug("in function addTodo()")
    rawline = addTodo_CollectContent()
    log.info("now building new ToDo")
    new_todo = ""

    confirm_todo = input("do you want to save\n\n   "+rawline+"\ny/n?\n")
    if confirm_todo == 'y':
        try:
            log.info("adding '"+rawline+"' to list")
            new_todo = Todo.Todo(rawline)
            # not appending yet, but rebuilding existing todos from a fresh copy from the file todo.txt
            # in order to prevent overwrting changes made manually to the file
            #todo_list.append(new_todo)
        except Exception as e:
            log.critical("was not able to build todo")
            print(e)
            pass
        try:
            print("saving to file %s....\n" % config.todotxt)
            log.info("rebuilding todo list from: %s" % config.todotxt)
            todo_list = tdt.buildIt(config.todotxt,"Todos")
            log.info("appending new todo")
            todo_list.append(new_todo)
            log.info("sorting new todo list")
            todo_list = sortTodos(todo_list,False, "status", "urgency", "priority")
            log.info("saving new todo list")
            tdt.save_state(todo_list)
            return todo_list
        except Exception as e:
            log.error("something went wrong while saving file")
            print("ERROR: "+str(e))
        log.critical("ToDo: add verification to individual entries")
    else:
        print("aborting...")

def buildListOfListsWithTodoProperties(listOfTodos,PropertiesToExtract,descriptionLimiter):
    # returns something like that: (todo: come up with better comment)
    # ListOfLists = [["a","b","c"],["a","b","c"],["a","b","c"]]
    ListOfLists = []
    for todo in listOfTodos:
        TodoPropertiesList = []
        for myproperty in PropertiesToExtract:
            if myproperty == 'description':
                description = getattr(todo,myproperty)
                shortDescription = description[0:descriptionLimiter].strip()
                TodoPropertiesList.append(shortDescription)
            elif type(getattr(todo,myproperty)) == list:
                list_to_string = ", ".join([item for item in getattr(todo,myproperty)])
                TodoPropertiesList.append(list_to_string)
            else:
                TodoPropertiesList.append(getattr(todo,myproperty))
        ListOfLists.append(TodoPropertiesList)
    return ListOfLists

def sortTodos(todos,reverse_arg=False,*sort_by):

    """
    :param todos:
    :param sort_by: ID, rawline, priority urgency status createDate finishDate dueDate description contexts projects size recurring
    :return:
    """
    # reverse arguments. last one must go first
    # this is done by starting with the length -1, going to 0, by stepping -1
    for i in range(len(sort_by)-1,-1,-1):
        try:
            todos.sort(key=lambda x: getattr(x, sort_by[i]), reverse=reverse_arg)
        except Exception as e:
            pass
            #print(e,sort_by[i])
    return todos

def listAllContexts(todo_list):
    log.debug("in function listAllContexts()")
    context_dict = {}
    for todo in todo_list:
        if todo.contexts:
            for context in todo.contexts:
                #context_list.append(context)
                if context not in context_dict:
                    context_dict[context] = 1
                else:
                    context_dict[context] +=1
    #implement sorting. but dicts are hairy to sort. find an elegant way
    # maybe create a list of tuples
    log.info("sorting dictionary")
    sorted_list_from_dict = sorted(context_dict.items(), key=itemgetter(1), reverse=True)
    sorted_dict = {}
    for tuple in sorted_list_from_dict:
        log.debug(type(tuple))
        log.debug(tuple[0])
        log.debug(tuple[1])
        sorted_dict[tuple[0]] = tuple[1]
    log.debug(sorted_dict)
    return sorted_dict

def listByContext(todo_list, journal_list, info_list, context, connect=False):

    log.debug("in function listByContext")
    result = []
    context = "".join(["@",context])
    for todo in todo_list:
        try:
            if context in todo.contexts:
                result.append(todo)
        except Exception as e:
            pass
    if connect is False:
        return result
    # this will only be executed if mode is 'connect=True'
    else:
        result = buildConnectionTable(result, context, journal_list, info_list)
        return result

def listByLabel(todo_list, label, journal_list = [], info_list = [], connect=False):
    log.info("in function listByLabel() with label "+label+" and connect flag "+str(connect))
    result = []
    label = "".join(["+",label])
    for todo in todo_list:
        try:
            log.debug("in for loop within todo_list, looking for label "+label+" in property Todo.projects")
            if label in todo.projects:
                log.debug("label "+label+" found, appending entire object to list result")
                result.append(todo)
        except Exception as e:
            log.debug("encountered error in listByLabel")
            pass
    result = sortTodos(result,"status","urgency","priority","createDate")
    if connect is False:
        return result
    # this will only be executed if mode is 'connect=True'
    else:
        result = buildConnectionTable(result, label, journal_list, info_list)
        return result

def listAllLabels(todo_list, drawtable):
    log.debug("in function listAllLabels")
    labels_list = []
    for todo in todo_list:
        if todo.projects:
            for label in todo.projects:
                labels_list.append(label)
    labels_list = set(labels_list)
    labels_list = sorted(labels_list)
    return labels_list

def listByStatus(todo_list, status):
    log.debug("in function listByStatus")
    result_list = []
    for todo in todo_list:
        try:
            if todo.status == status:
                result_list.append(todo)
        except Exception as e:
            print("Error", e, vars(todo))
    log.info("returning result list from listByStatus()")
    return result_list

def listBySize(todo_list, size,status):
    log.debug("listing by size")
    result_list = []
    for todo in todo_list:
        try:
            if todo.size == size and todo.status in status:
                result_list.append(todo)
        except Exception as e:
            log.info("listing by size failed due to :"+e)
    log.info("list by size "+size+" resulted in "+str(len(result_list))+" results")
    return result_list

def listByPrio(prio,todo_list,status = "open"):
    log.debug("in function listByPrio")
    if not status: status = input("status open or done\n")
    prio = "("+prio+")"
    prioTodos = []
    for todo in todo_list:
        try:
            if todo.priority == prio and todo.status == status:
                prioTodos.append(todo)
        except Exception as e:
            print("Error", e)
    return prioTodos

def listByUrgency(todo_list, urgency):
    global config
    log.debug("in function listByUrgency")
    status = "open" #input("status open or done\n")
    urgency_todos = []
    for todo in todo_list:
        try:
            if todo.urgency == urgency and todo.status == status:
                urgency_todos.append(todo)
        except Exception as e:
            print("Error", e)
    return urgency_todos

def listByManualQuery(queryObj,todo_list):
    global config
    log.debug("in function byManualQuery")
    result_list = []
    for todo in todo_list:
        # these are 'and' relations. 'OR' is not in yet
        if todo.priority in queryObj.priority:
            if todo.status in queryObj.status:
                if todo.urgency in queryObj.urgency:
                    result_list.append(todo)
        else:
            pass
    return result_list

def connected_list(todo_list, journal_list, info_list,labels_or_contexts):
    # this will be returned
    todo_list_filtered = []
    # adapt journal and infos a bit first
    for item in journal_list:
        item.priority = "Journal"
        item.urgency = ""
        item.status = ""
    for item in info_list:
        item.priority = "Info"
        item.urgency = ""
        item.status = ""
    # pre-sorting lists before merging
    # todos don't necessarily have createDates. sorting on those will raise exception
    try:
        todo_list_sorted = sortTodos(todo_list, "createDate")
    except TypeError as e:
        print("couldn't sort because of: ",str(e))
        log.error("couldn't sort because of: ",str(e))
    journal_list_sorted = sortTodos(journal_list,"createDate")
    info_list_sorted = sortTodos(info_list,"createDate")
    # merging lists
    uber_list = todo_list_sorted+journal_list_sorted+info_list_sorted
    def getAllContextsAndProjects(entry):
        listOfContextsAndProjects = []
        try:
            for project in entry.projects:
                listOfContextsAndProjects.append(project[1:])
            for context in entry.contexts:
                listOfContextsAndProjects.append(context[1:])
        except TypeError:
            # entry did not have projects or contexts set
            pass
        return listOfContextsAndProjects
    for l_or_c in labels_or_contexts.split(" "):
        for entry in uber_list:
            listOfContextsAndProjects = getAllContextsAndProjects(entry)
            # stripping the '+' and '@' from the attributes projects (label) and context
            if l_or_c in listOfContextsAndProjects:
                todo_list_filtered.append(entry)
    # removing duplicates
    todo_list_unique = set(todo_list_filtered)
    todo_list_filtered_unique = list(todo_list_unique)
    todo_list_final = sortTodos(todo_list_filtered_unique,"createDate")
    return todo_list_final

def buildConnectionTable(result,context_or_label,journal_list,info_list):
    log.info("noodling through jounnal_list, looking for " + context_or_label + " and cleaning table fields")
    for journalentry in journal_list:
        try:
            if context_or_label in journalentry.projects or context_or_label in journalentry.contexts:
                journalentry.priority = "Journal"
                journalentry.urgency = ""
                journalentry.status = ""
                # adding matching journal object to global todo_list
                result.append(journalentry)
        except:
            log.debug("some error encountered while noodling through journal_list, but passing it")
            pass
    log.info("noodling through info_list, looking for " + context_or_label + " and cleaning table fields")
    for info in info_list:
        try:
            if context_or_label in info.projects or context_or_label in info.contexts:
                info.priority = "Info"
                info.urgency = ""
                info.status = ""
                # adding matching info object to global todo_list
                result.append(info)
        except:
            log.debug("some error encountered while noodling through info_list, but passing it")
            pass
    log.info("done, returning resultlist of length " + str(len(result)))
    return result
