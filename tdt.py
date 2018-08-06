# -*- coding: iso-8859-1 -*-

import threading
import time

import datetime
from Todo import Todo
import Classes
from tableoutput import *
from operator import itemgetter, attrgetter, methodcaller
import helpers


"""
Todos:
* add recurring to table (done for Todo Object)
* Add testing
"""

def background():
    while True:
        time.sleep(10)
        #print('disarm me by typing exit')

def save_state():
    #todo: add sorting by prio of entire list
    #filepath = "Files/todo.txt"
    filepath = config.todotxt

    log.info('saving all objects to: '+filepath)
    log.debug("size of todo_list is")
    log.debug(str(len(todo_list)))
    if len(todo_list)>0:
        with open(filepath,"w", encoding='UTF-8') as file:
            log.info("function save_state, writing to " + str(file))
            log.warning("TODO: implement urgency like priority and others")
            for todo in todo_list:
                try:
                    file.write(todo.rawline.strip()+"\n")
                except Exception as e:
                    log.critical("saving to file failed miserably")
                    print(e)
    else:
        print("something is wrong. exiting to prevent overwriting todo list with zero content")
        log.critical("exiting due to zero length todo_list")
        exit()


def listAllContexts(todo_list):
    log.info("in function listAllContexts()")
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

def listByContext(todo_list, context, connect=False):
    log.info("in function listByContext")
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
        result = helpers.buildConnectionTable(result, context, journal_list, info_list)
        return result

def listByLabel(todo_list,label,connect=False):
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
    result = helpers.sortTodos(result,"urgency","priority","createDate")
    if connect is False:
        return result
    # this will only be executed if mode is 'connect=True'
    else:
        result = helpers.buildConnectionTable(result, label, journal_list, info_list)
        return result


def listAllLabels(todo_list, drawtable):
    log.info("in function listAllLabels")
    labels_list = []
    for todo in todo_list:
        if todo.projects:
            for label in todo.projects:
                labels_list.append(label)
    labels_list = set(labels_list)
    labels_list = sorted(labels_list)
    table = labelTable(labels_list, drawtable)
    return labels_list


def listByStatus(status,todo_list):
    log.info("in function listByStatus")
    result_list = []
    for todo in todo_list:
        try:
            if todo.status == status:
                #print("".join([todo.priority,"\t",todo.description.strip()]))
                result_list.append(todo)
        except Exception as e:
            print("Error", e, vars(todo))
    log.info("returning result list from listByStatus()")
    return result_list

def listByPrio(prio,todo_list):
    log.info("in function listByPrio")
    status = input("status open or done\n")
    prio = "("+prio+")"
    prioTodos = []
    for todo in todo_list:
        try:
            if todo.priority == prio and todo.status == status:
                prioTodos.append(todo)
        except Exception as e:
            print("Error", e)
    return prioTodos

def listByUrgency(urgency,todo_list):
    log.info("in function listByUrgency")
    status = "open" #input("status open or done\n")
    #prio = urgency
    urgencyTodos = []
    for todo in todo_list:
        try:
            if todo.urgency == urgency and todo.status == status:
                urgencyTodos.append(todo)
        except Exception as e:
            print("Error", e)
    return urgencyTodos

def sortBy(todo_list, urgency=False):
    log.info("in function sortBy")
    s = sorted(todo_list, key=attrgetter('priority'))
    if urgency:
        s = sorted(s, key=attrgetter('urgency'))
    sorted_todo_list = sorted(s, key=attrgetter('status'), reverse=True)
    log.info("returning, not drawing, final table")
    todo_list = sorted_todo_list
    return todo_list

def addTodo():
    log.info("in function addTodo()")
    # pulling up global todo_list to be referenced in substituion in sorting later
    global todo_list
    rawline = helpers.addTodo_CollectContent()
    log.info("now building new ToDo")

    confirmTodo = input("do you want to save\n\n   "+rawline+"\ny/n?\n")
    if confirmTodo == 'y':
        try:
            log.info("adding '"+rawline+"' to list")
            newTodo = Todo(rawline)
            todo_list.append(newTodo)
        except Exception as e:
            log.critical("was not able to build todo")
            print(e)
            pass
        log.info("sorting todo_list")
        try:
            # sort here (new function sortBy())
            #todo_list = sortBy(todo_list)#, urgency = True)
            todo_list = helpers.sortTodos(todo_list,"urgency","priority")
        except Exception as e:
            log.critical("sorting did not work")
            print(e)
            pass
        try:
            print("saving to file....\n")
            save_state()
        except Exception as e:
            log.error("something went wrong while saving file")
            print(e)
        log.critical("ToDo: extend modificaiton to existing todos to make it really useful")
        log.critical("ToDo: add verification to individual entries")
    else:
        print("aborting...")

def updateTodo(choice = ""):
    log.info("in function updateTodo")
    #choice = ""
    try:
        if choice == "":
            choice = int(input("enter int(ID) to update or 'ls' to list todos\n"))
        log.debug("if input was not an integer, exception is thrown and caught below")
        found = False
        for todo in todo_list:
            if todo.ID == choice:
                found = True
                resultTable([todo],100000,False,200)
                action = input("\nAvailable modification commands:\n\n"
                               "*  <x> for resolving\n"
                               "*  <prio A-Z> to change priority\n"
                               "*  <u>rgency 0-3\n"
                               "*  <due yyyy-mm-dd>\n"
                               "*  <size xs-xxl> to change size\n"
                               "*  <a>dd arbitrary text to rawline\n" 
                               "*  e to exit to main menu\n\n")
                # -------------------------------------------------------------------------------------------#
                if action == 'x':
                    resolutionComment = input("do you want to add a comment? (will be appended with '-->')\n")
                    if len(resolutionComment) > 0:
                        resolutionComment = " --> "+resolutionComment

                    log.info("resolving todo with id " + str(todo.ID))
                    todo.status = 'done'
                    todo.finishDate = datetime.datetime.now().strftime("%Y-%m-%d")
                    log.info("object properties set accordingly")
                    log.info("now updating rawline directly (not calling updateRawLine) ")
                    todo.rawline = " ".join(["x",todo.finishDate.strip(),todo.rawline.strip(),resolutionComment.strip()])
                    log.info(todo.rawline)
                    updateTodo(choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('prio'):
                    log.info("setting prio from "+todo.priority+" to "+action)
                    todo.priority = "("+str(action).split(" ")[1].upper()+")"
                    log.debug(todo.rawline)
                    todo.updateRawline(r"\([A-Z]\)","("+str(action).split(" ")[1].upper()+")")
                    log.info(todo.rawline)
                    updateTodo(choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('u'):
                    log.info("setting urgency from "+todo.urgency+" to "+action)
                    todo.urgency = str(action).split(" ")[1]
                    log.info(todo.rawline)
                    # need to update (replace or append) rawline, otherwise the modification is lost
                    todo.updateRawline(r"\{[0-3]\}", "{"+str(action).split(" ")[1]+"}")
                    log.info(todo.rawline)
                    updateTodo(choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('due'):
                    log.info("setting due date")
                    todo.dueDate = action.split(" ")[1]
                    log.info(todo.rawline)
                    todo.updateRawline(r"due\:\s?\d\d\d\d-\d\d-\d\d","due:"+todo.dueDate)
                    log.info(todo.rawline)
                    updateTodo(choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('s'):
                    log.info("setting size")
                    todo.size = action.split(" ")[1].replace("$$","").upper()
                    log.info(todo.rawline)
                    todo.updateRawline(r"\$\$([a-zA-Z]*)","$$"+todo.size)
                    log.info(todo.rawline)
                    updateTodo(choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('a'):
                    log.info("adding arbitrary text to rawline")
                    log.info(todo.rawline)
                    stringToAdd = action[1:]
                    todo.rawline = todo.rawline.strip()

                    todo.rawline += stringToAdd
                    log.info(todo.rawline)
                    save_state()
                    updateTodo(choice)
                # -------------------------------------------------------------------------------------------#
                elif action == 't':
                    # pyperclip.copy(todo.description)
                    # text = input("ctrl-v to paste full text to edit\n")
                    # todo.description = text
                    log.error("changing description is not implemeneted")
                    print("not implemented yet, sorry")
                    pass
                # -------------------------------------------------------------------------------------------#
                elif action == 'e':
                    log.info("exiting to main menu")
                    break
                # -------------------------------------------------------------------------------------------#
                else:
                    print("the computer says 'nooo'")
                    log.info("invalid entry, restart")
                resultTable([todo])
                save_state()
            else:
                log.debug("no match for ID")
        if found == False:
            log.error("Entered ID "+str(choice)+" does not exist")
            print("ID not found")

    except ValueError:
        #schlau gemacht. wenn choice kein integer ist, wirf exception.
        #in exception, zeige alle offenen todos
        #trick am schluss: die funktion startet sich selbst wieder. so lange bis eine ID eingegeben wird
        log.warning("no valid ID ([h]int!) entered, listing all open todos")
        print("no validid given, listing all open todos:\n\n")
        list_for_table = []
        log.info("showing table of all open todos, giving user an overview")
        for todo in todo_list:
            if todo.status == 'open':
                list_for_table.append(todo)
        resultTable(list_for_table)
        log.info("calling updatetodo again")
        updateTodo()

def resolvedWithinDays(NumOfDays,todo_list):
    # returns list of objects which meet the criteria
    log.info("in function resolvedWithinDAys")
    resultList = []
    today = datetime.date.today()
    startdate = today - datetime.timedelta(NumOfDays)
    try:
        for todo in todo_list:
            if todo.finishDate is not None:
                #convert str to date object
                log.debug('constructing date from string')
                log.debug('comparing today with reconstructed todo date')
                if todo.finishDate <= today and todo.finishDate >= startdate:
                    resultList.append(todo)
        log.info('returning result list of length: ' +str(len(resultList)))
        return resultList
    except Exception as e:
        log.error("'resolvedWithinDays' had a problem")
        log.error(e)
        print("failed, please check log file" )

def addedWithinDays(NumOfDays,todo_list):
    # todo simplify and merge with resolved
    # returns list of objects which meet the criteria
    log.info("in function addedWithinDays")
    resultList = []
    today = datetime.date.today()
    startdate = today - datetime.timedelta(NumOfDays)
    try:
        for todo in todo_list:
            if todo.createDate is not None:
                #convert str to date object
                #log.debug('constructing date from string')
                #dateList = todo.createDate.split("-")
                #todoAddedDate = datetime.date(int(dateList[0]),int(dateList[1]),int(dateList[2]))
                #log.debug('comparing today with reconstructed todo date')
                if todo.createDate <= today and todo.createDate >= startdate:
                    resultList.append(todo)
        log.info('returning result list of length: ' +str(len(resultList)))
        return resultList
    except Exception as e:
        log.error("'resolvedWithinDays' had a problem")
        log.error(e)
        print("failed, please check log file" )

def destroyObjects(objLists):
    log.info("in function destroyObjects")
    for list in objLists:
        for obj in list:
            print("now destructing obj", obj, type(obj))
            del list.obj

def byManualQuery(queryObj,todo_list):
    log.info("in function byManualQuery")
    print("query is : ", vars(queryObj))
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

def connect_all():
    log.info("menu option 'connect'")
    print('connecting todos with journal and info\n')
    global journal_list
    log.info("building journal list")
    #journal_list = buildIt("../../Lists2/journal.txt", "Journal")
    journal_list = buildIt(config.journaltxt, "Journal")

    global info_list
    log.info("building info_list")
    #info_list = buildIt("../../Lists2/info.txt", "Info List")
    info_list = buildIt(config.infotxt, "Info List")

    log.info("user input choice 'label or context'")
    list_or_context = input("label or context? ('l' vs 'c')\n")
    # -------------------------------------------------------------------------------------------#
    if list_or_context == 'l':
        log.info("user choice 'l' for label")
        label = input("enter label/tag to list (without '+') \n")
        try:
            log.info("calling listByLabel() with user input label " + label)
            result = listByLabel(todo_list, label, True)
            # resultTable(result)
        except Exception as e:
            log.error("error " + str(e) + " encountered in calling listByLabel with Label " + label)
            print(e)
    # -------------------------------------------------------------------------------------------#
    elif list_or_context == 'c':
        label = input("enter context to list (without '@') \n")
        try:
            result = listByContext(todo_list, label, True)
            # resultTable(result)
        except Exception as e:
            print(e)
    else:
        print("invalid input, exiting")
        log.info("invalid user input")

    try:
        resultTable(result, 10000, False, 200)  # content, limiter ,return tableobj, width
        log.info("asking if user wants to export")
        export = input("do you want to export this? y/n\n")
        # -------------------------------------------------------------------------------------------#
        if export == 'n':
            log.info("no export. cancelling")
            pass
        # -------------------------------------------------------------------------------------------#
        elif export == 'y':
            log.info("exporting connected list")
            exportThis(result)
        else:
            print("invalid entry")
    except:
        # catching the case when something went wrong drawing the table
        log.critical("something went wrong while writing the result table")
        pass

def main_menu():
    log.debug("in function main_menu()")
    global todo_list
    entry = input(
        "\n"
        "type:\n\n"
        "*  exit\n"
        "*  connect (c)\n"
        "*  options (o)\n"
        "*  list (l)\n"
        "*  add (a)\n"
        "*  modify (m)\n"
    )
    # -------------------------------------------------------------------------------------------#
    # -------------------------------------------------------------------------------------------#
    if entry == 'exit' or entry == 'e':
        log.info("----------------- user exit ------------------")
        print('Saving current state...\nQuitting Plutus. Goodbye!')
        save_state()
        sys.exit()
    # -------------------------------------------------------------------------------------------#
    # -------------------------------------------------------------------------------------------#
    elif entry == 'connect' or entry == 'c':
        connect_all()
    # -------------------------------------------------------------------------------------------#
    # -------------------------------------------------------------------------------------------#
    elif entry == 'options' or entry == 'o':
        option = input("*  [wip]rebuild (r)\n"
                       "*  [wip]test\n"
                       "*  dump (d)\n"
                       "*  dumptable (dt)\n\n")
        # -------------------------------------------------------------------------------------------#
        if option == 'rebuild' or option == 'r':  # (if list changed externally)':
            todo_list = buildIt(config.todotxt, "Todo List")
        # -------------------------------------------------------------------------------------------#
        elif option == 'dump' or option == 'd':
            print("\nlenght of list: ", len(todo_list))
            for obj in todo_list:
                print(vars(obj))
        # -------------------------------------------------------------------------------------------#
        elif option == 'dumptable' or option == 'dt':
            print("\nlenght of list: ", len(todo_list))
            resultTable(todo_list)
    # -------------------------------------------------------------------------------------------#
    # -------------------------------------------------------------------------------------------#
    elif entry == 'list' or entry == 'l':
        helpers.writeMenu_list(todo_list)
        """
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
            "*  added last n days (a <days>\n"
            "*  resolved last n days (r <days>)\n\n"
            "*  eisenhower (e)\n")
        # -------------------------------------------------------------------------------------------#
        if list == 'contexts' or list == 'c':
            log.debug("listing all contexts")
            context_dict = listAllContexts(todo_list)
            log.debug("content of context dict")
            log.debug(type(context_dict))
            log.info("building table object")
            newTable = TableObj()
            newTable.numOfCols = 2
            newTable.colHeaders = ["context", "count"]
            newTable.content = context_dict
            tableFromTableObj(newTable,True)
        # -------------------------------------------------------------------------------------------#
        elif list.startswith("lq"):
            print("something like u=1,2 p=a,b s=o|d")
            query = list.replace("lq ", "")
            query = query.split(" ")
            myQuery = Query(query)
            filtered_list = byManualQuery(myQuery)
            resultTable(filtered_list)
        # -------------------------------------------------------------------------------------------#
        elif list == 'eisenhower' or list == 'e':
            eisenhower(todo_list)
        # -------------------------------------------------------------------------------------------#
        elif list == 'labels' or list == 'l':
            listAllLabels(todo_list)
        # -------------------------------------------------------------------------------------------#
        elif list == 'ls context' or list == 'lc':
            context = input('context without @ but accurate cases\n')
            try:
                result = listByContext(context)
                resultTable(result)
            except Exception as e:
                print(e)
        # -------------------------------------------------------------------------------------------#
        elif list == 'll' or list == 'ls label':
            label = input('label without +, but accurate cases\n')
            try:
                result = listByLabel(todo_list, label)
                resultTable(result)
            except Exception as e:
                print(e)
        # -------------------------------------------------------------------------------------------#
        elif list == "status" or list == 'ls':
            log.debug("running with option list->status (ls)")
            status = input("status. 'open' or 'done'\n")
            log.info("calling listByStatus(status) with status " + status)
            result = listByStatus(status)
            log.info("result is set to" + str(len(result)))
            resultTable(result)
        # -------------------------------------------------------------------------------------------#
        elif list == "ls prio" or list == 'lp':
            prio = input("a-z\n")
            resultTable(listByPrio(prio.upper()))
        # -------------------------------------------------------------------------------------------#
        elif list == "urgency" or list == 'u':
            urgency = input("1-3\n")
            resultTable(listByUrgency(urgency))
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
            table_content = resolvedWithinDays(days)
            resolved_table = TableObj()
            resolved_table.width = 300
            resolved_table.numOfCols = 9
            resolved_table.colHeaders = ["ID", "P", "U", "Created","Resolved","Description","Context","Tags","Size"]
            propertiesToExtract = ["ID", "priority", "urgency", "createDate","finishDate","description","contexts","projects","size"]

            resolved_table.content = helpers.buildListOfListsWithTodoProperties(table_content,propertiesToExtract, resolved_table.descriptionLimiter)
            tableFromTableObj(resolved_table,True)

            log.info('done. returning to menu')
            """
    # -------------------------------------------------------------------------------------------#
    # -------------------------------------------------------------------------------------------#
    elif entry == 'add' or entry == 'a':
        addTodo()
    # -------------------------------------------------------------------------------------------#
    # -------------------------------------------------------------------------------------------#
    elif entry == 'modify' or entry == 'm':
        updateTodo()

    else:
        print("unrecognized input. please try again")
        log.error("user input "+entry+" is invalid")


def buildIt(filepath, source):
    log.info("in function 'buildIt(), generating from "+filepath +" and source "+source )
    #open todo file and generate objects and put them into list
    with open(filepath, "r", encoding='UTF-8') as file:
        lines = file.readlines()
    todo_list = []
    for item in lines:
        try:
            newTodo = Todo(item)
            todo_list.append(newTodo)
        except Exception as e:
            print("Whatever",e)
            pass
    print(source, " built. Total number of items: %d" % len(todo_list))
    return todo_list

def main():
    log.debug("in function main")
    log.info("starting threading")
    # now threading1 runs regardless of user input
    threading1 = threading.Thread(target=background)
    threading1.daemon = True
    threading1.start()
    global todo_list
    log.info("reading todo.txt")
    todo_list = buildIt(config.todotxt, "Todo List")

    while True:
        log.debug("writing menu")
        main_menu()


if __name__ == "__main__":

    format_string = '%(asctime)s: %(levelname)s: %(message)s'

    log.basicConfig(filename='debug.log', level=log.INFO, format=format_string)
    log.info("---------------- starting ----------------")
    config = Classes.Config()
    log.warning("TODO: nothing")
    todo_list = []
    log.debug("empty todo_list global var created")
    journal_list = []
    log.debug("empty journal_list global var created")
    info_list = []
    log.debug("empty info_list global var created")
    log.debug("now calling main()")
    main()


