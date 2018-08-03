import datetime
import logging as log
import tdt
import Classes
import tableoutput as table
from operator import attrgetter

# wrapping input to use mock.patch in unittest as suggested by
# https://stackoverflow.com/questions/21046717/python-mocking-raw-input-in-unittests
def get_input(prompt):
    return input(prompt)

def addTodo_CollectContent():
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

def writeMenu_list(todo_list):
    list = input(
        "*  list all (c)ontexts\n"
        "*  list by context (lc)\n"
        "*  list all (l)abels\n"
        "*  list by label (ll)\n"
        "*  list by status (ls)\n"
        "*  list by prio (lp)\n"
        "*  list by query (lq)\n"
        "*  list by urgency (u)\n"
        "*  list today, this week, this month this year (TODO)\n"
        "*  list by big Goals (TODO)\n"
        "*  added last n days (a <days>)\n"
        "*  resolved last n days (r <days>)\n\n"
        "*  eisenhower (e)\n")
    # -------------------------------------------------------------------------------------------#
    if list == 'contexts' or list == 'c':
        log.debug("listing all contexts")
        context_dict = tdt.listAllContexts(todo_list)
        log.debug("content of context dict")
        log.debug(type(context_dict))
        log.info("building table object")
        newTable = Classes.TableObj()
        newTable.numOfCols = 2
        newTable.colHeaders = ["context", "count"]
        newTable.content = context_dict
        table.tableFromTableObj(newTable, True)
    # -------------------------------------------------------------------------------------------#
    elif list.startswith("lq"):
        print("something like u=1,2 p=a,b s=o|d")
        query = list.replace("lq ", "")
        query = query.split(" ")
        myQuery = Classes.Query(query)
        filtered_list = tdt.byManualQuery(myQuery,todo_list)
        table.resultTable(filtered_list)
    # -------------------------------------------------------------------------------------------#
    elif list == 'eisenhower' or list == 'e':
        tdt.eisenhower(todo_list)
    # -------------------------------------------------------------------------------------------#
    elif list == 'labels' or list == 'l':
        tdt.listAllLabels(todo_list,True)
    # -------------------------------------------------------------------------------------------#
    elif list == 'ls context' or list == 'lc':
        context = input('context without @ but accurate cases\n')
        try:
            result = tdt.listByContext(todo_list,context)
            table.resultTable(result)
            print("number of hits:"+str(len(result)))
        except Exception as e:
            print(e)
    # -------------------------------------------------------------------------------------------#
    elif list == 'll' or list == 'ls label':
        label = input('label without +, but accurate cases\n')
        try:
            result = tdt.listByLabel(todo_list, label)
            table.resultTable(result)
        except Exception as e:
            print(e)
    # -------------------------------------------------------------------------------------------#
    elif list == "status" or list == 'ls':
        log.debug("running with option list->status (ls)")
        status = input("status. 'open' or 'done'\n")
        log.info("calling listByStatus(status) with status " + status)
        result = tdt.listByStatus(status,todo_list)
        log.info("result is set to" + str(len(result)))
        table.resultTable(result)
    # -------------------------------------------------------------------------------------------#
    elif list == "ls prio" or list == 'lp':
        prio = input("a-z\n")
        table.resultTable(tdt.listByPrio(prio.upper(),todo_listl))
    # -------------------------------------------------------------------------------------------#
    elif list == "urgency" or list == 'u':
        urgency = input("1-3\n")
        table.resultTable(tdt.listByUrgency(urgency,todo_list))
    # -------------------------------------------------------------------------------------------#
    elif list.startswith("r"):
        log.debug('chose resolved within days')
        try:
            days = int(list.split(" ")[1])
        except IndexError:
            log.warning('invalid input, setting to 0 (today)')
            days = 0
        # the old, static way of building a table
        # resultTable(resolvedWithinDays(days))

        # testing building the same with tableobj
        table_content = tdt.resolvedWithinDays(days,todo_list)
        resolved_table = Classes.TableObj()
        resolved_table.width = 300
        resolved_table.numOfCols = 9
        resolved_table.colHeaders = ["ID", "P", "U", "Created", "Resolved", "Description", "Context", "Tags", "Size"]
        propertiesToExtract = ["ID", "priority", "urgency", "createDate", "finishDate", "description", "contexts",
                               "projects", "size"]

        resolved_table.content = buildListOfListsWithTodoProperties(table_content, propertiesToExtract, resolved_table.descriptionLimiter)
        table.tableFromTableObj(resolved_table, True)

        log.info('done. returning to menu')
    # -------------------------------------------------------------------------------------------#

    elif list.startswith("a"):
        # todo simplify and merge with resolved
        log.debug('chose added within days')
        try:
            days = int(list.split(" ")[1])
        except IndexError:
            log.warning('invalid input, setting to 0 (today)')
            days = 0
        # the old, static way of building a table
        # resultTable(resolvedWithinDays(days))

        # testing building the same with tableobj
        table_content = tdt.addedWithinDays(days,todo_list)
        added_table = Classes.TableObj()
        added_table.width = 300
        added_table.numOfCols = 9
        added_table.colHeaders = ["ID", "P", "U", "Created", "Resolved", "Description", "Context", "Tags", "Size"]
        propertiesToExtract = ["ID", "priority", "urgency", "createDate", "finishDate", "description", "contexts",
                               "projects", "size"]

        added_table.content = buildListOfListsWithTodoProperties(table_content, propertiesToExtract, added_table.descriptionLimiter)
        table.tableFromTableObj(added_table, True)

        log.info('done. returning to menu')

def sortTodos(todos,sort_by):
    def listit(todos):
        for todo in todos:
            print(todo.ID, todo.createDate, todo.urgency)
    print('origial')
    listit(todos)
    todos.sort(key=lambda x: x.createDate, reverse=False)
    print('createdate')

    listit(todos)
    """
    todos.sort(key=lambda x: x.priority)
    print('priority')

    listit(todos)
    """
    return todos
    #todo add sorting of todolist with arbitrary number of sort keys