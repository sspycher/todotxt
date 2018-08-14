# -*- coding: iso-8859-1 -*-

import threading
import time
import logging as log
import datetime
from Todo import Todo
import Classes
import tableoutput as table
from operator import itemgetter, attrgetter, methodcaller
import helpers
import sys

# declaring global variable config
config = Classes.Config()
unsaved_changes = []

"""
Todos:
* add recurring to table (done for Todo Object)
* Add testing
"""

def background():
    while True:
        time.sleep(10)
        #print('disarm me by typing exit')

def save_state(todo_list):
    #todo: add sorting by prio of entire list
    #filepath = "Files/todo.txt"
    global config
    filepath = config.todotxt
    print(filepath)
    log.debug("todolist id is " + str(id(todo_list)))
    log.info('saving all objects to: '+filepath)
    log.debug("size of todo_list is")
    log.debug(str(len(todo_list)))
    if len(todo_list)>0:
        print("wrting to file %s" %filepath)
        with open(filepath,"w", encoding='UTF-8') as file:
            log.info("function save_state, writing to " + str(file))
            for todo in todo_list:
                try:
                    file.write(todo.rawline.strip()+"\n")
                except Exception as e:
                    log.critical("saving to file failed miserably")
                    print(e)
            # resetting todo_list

        del todo_list
        # rebuilding from scratch
        todo_list = buildIt(config.todotxt,"Todos")
        log.debug("todolist id is " + str(id(todo_list)))

    else:
        print("something is wrong. exiting to prevent overwriting todo list with zero content")
        log.critical("exiting due to zero length todo_list")
        exit()

def sortBy(todo_list, urgency=False):
    global config
    log.debug("in function sortBy")
    s = sorted(todo_list, key=attrgetter('priority'))
    if urgency:
        s = sorted(s, key=attrgetter('urgency'))
    sorted_todo_list = sorted(s, key=attrgetter('status'), reverse=True)
    log.info("returning, not drawing, final table")
    todo_list = sorted_todo_list
    return todo_list

def updateTodo(todo_list, choice = ""):
    global config
    log.debug("in function updateTodo")
    #choice = ""
    try:
        if choice == "":
            choice = int(input("enter int(ID) to update or 'ls' to list todos\n"))
        log.debug("if input was not an integer, exception is thrown and caught below")
        found = False
        for todo in todo_list:
            if todo.ID == choice:
                found = True
                table.resultTable([todo],100000,False,200)
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
                    save_state(todo_list)
                    updateTodo(todo_list, choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('prio'):
                    log.info("setting prio from "+todo.priority+" to "+action)
                    todo.priority = "("+str(action).split(" ")[1].upper()+")"
                    log.debug(todo.rawline)
                    todo.updateRawline(r"\([A-Z]\)","("+str(action).split(" ")[1].upper()+")")
                    log.info(todo.rawline)
                    save_state(todo_list)
                    updateTodo(todo_list, choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('u'):
                    log.info("setting urgency from "+todo.urgency+" to "+action)
                    todo.urgency = str(action).split(" ")[1]
                    log.info(todo.rawline)
                    # need to update (replace or append) rawline, otherwise the modification is lost
                    todo.updateRawline(r"\{[0-3]\}", "{"+str(action).split(" ")[1]+"}")
                    log.info(todo.rawline)
                    save_state(todo_list)
                    updateTodo(todo_list, choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('due'):
                    log.info("setting due date")
                    todo.dueDate = action.split(" ")[1]
                    log.info(todo.rawline)
                    todo.updateRawline(r"due\:\s?\d\d\d\d-\d\d-\d\d","due:"+todo.dueDate)
                    log.info(todo.rawline)
                    save_state(todo_list)
                    updateTodo(todo_list, choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('s'):
                    log.info("setting size")
                    todo.size = action.split(" ")[1].replace("$$","").upper()
                    log.info(todo.rawline)
                    todo.updateRawline(r"\$\$([a-zA-Z]*)","$$"+todo.size)
                    log.info(todo.rawline)
                    save_state(todo_list)
                    updateTodo(todo_list, choice)
                # -------------------------------------------------------------------------------------------#
                elif str(action).startswith('a'):
                    log.info("adding arbitrary text to rawline")
                    log.info(todo.rawline)
                    stringToAdd = action[1:]
                    todo.rawline = todo.rawline.strip()

                    todo.rawline += stringToAdd
                    todo.setDescription(todo.rawline)
                    log.info(todo.rawline)
                    log.debug("todolist id is "+str(id(todo_list)))
                    save_state(todo_list)
                    updateTodo(todo_list, choice)
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
                    table.resultTable([todo])
                # maybe delete this save todo
                save_state(todo_list)
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
        table.resultTable(list_for_table)
        log.info("calling updatetodo again")
        updateTodo(todo_list)

def resolvedWithinDays(NumOfDays,todo_list):
    global config
    # returns list of objects which meet the criteria
    log.debug("in function resolvedWithinDAys")
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
    global config
    # todo simplify and merge with resolved
    # returns list of objects which meet the criteria
    log.debug("in function addedWithinDays")
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
    global config
    log.debug("in function destroyObjects")
    for list in objLists:
        for obj in list:
            print("now destructing obj", obj, type(obj))
            del list.obj

def connect_all(todo_list):
    global config
    log.debug("todolist id is " + str(id(todo_list)))
    log.info("menu option 'connect'")
    print('connecting todos with journal and info\n')
    global journal_list
    log.info("building journal list")
    journal_list = buildIt(config.journaltxt, "Journal")

    global info_list
    log.info("building info_list")
    info_list = buildIt(config.infotxt, "Info List")

    log.info("user input choice 'label or context'")
    list_or_context = input("label or context? ('l' vs 'c')\n")
    # -------------------------------------------------------------------------------------------#
    if list_or_context == 'l':
        log.info("user choice 'l' for label")
        label = input("enter label/tag to list (without '+') \n")
        try:
            log.info("calling listByLabel() with user input label " + label)
            result = helpers.listByLabel(todo_list, label, journal_list, info_list, True)
        except Exception as e:
            log.error("error " + str(e) + " encountered in calling listByLabel with Label " + label)
            print(e)
    # -------------------------------------------------------------------------------------------#
    elif list_or_context == 'c':
        label = input("enter context to list (without '@') \n")
        try:
            result = helpers.listByContext(todo_list, journal_list, info_list, label, True)
        except Exception as e:
            print(e)
    else:
        print("invalid input, exiting")
        log.info("invalid user input")

    try:
        table.resultTable(result, 10000, False, 200)  # content, limiter ,return tableobj, width
        log.info("asking if user wants to export")
        export = input("do you want to export this? y/n\n")
        # -------------------------------------------------------------------------------------------#
        if export == 'n':
            log.info("no export. cancelling")
            pass
        # -------------------------------------------------------------------------------------------#
        elif export == 'y':
            log.info("exporting connected list")
            helpers.exportThis(result)
        else:
            print("invalid entry")
    except:
        # catching the case when something went wrong drawing the table
        log.critical("something went wrong while writing the result table")
        pass


def menu_display_input_options(options):
    choice = input(options)
    return choice

def writeMenu_main(todo_list, in_test_mode=False, menu_option=""):
    global config
    log.debug("in function main_menu()")
    if not in_test_mode:
        entry = input(
            "\n"
            "type:\n\n"
            "*  today (t)\n"
            "*  connect (c)\n"
            "*  options (o)\n"
            "*  list (l)\n"
            "*  add (a)\n"
            "*  modify (m)\n"
            "*  exit\n"
        )
    else:
        entry = menu_option

    def processChoice(entry):
        # -------------------------------------------------------------------------------------------#
        if entry == 'exit' or entry == 'e':
            log.info("----------------- user exit ------------------")
            main_exit()
        elif entry == 't':
            todos_today = main_today(todo_list)
            table.resultTable(todos_today)
            writeMenu_main(todo_list)
        elif entry == 'connect' or entry == 'c':
            todo_list_filtered = main_connect(todo_list)
            table.resultTable(todo_list_filtered, 10000, False, 200)
            helpers.export_CSV(todo_list_filtered)
            writeMenu_main(todo_list)
        elif entry == 'list' or entry == 'l':
            writeMenu_list(todo_list)
            writeMenu_main(todo_list,False,"l")
        elif entry == 'add' or entry == 'a':
            helpers.addTodo(todo_list)
            writeMenu_main(todo_list)
        else:
            # continue with rest of list choices
            pass
    # -------------------------------------------------------------------------------------------#
    # breaking the menu into smaller functions to enable E2E testability without mocking user input
    # -------------------------------------------------------------------------------------------#
    def main_exit(): #imported
        print('Saving current state...\nQuitting Plutus. Goodbye!')
        save_state(todo_list)
        sys.exit()

    def main_today(todo_list):
        print("due today")
        print("=========")
        todos_today = []
        for todo in todo_list:
            if todo.urgency == '0' and todo.status == 'open': todos_today.append(todo)
        return todos_today

    def main_connect(todo_list):
        global journal_list
        global info_list
        labels_or_contexts = input("what contexts or labels are you connecting? (space separated if multiple)\n")

        journal_list = buildIt(config.journaltxt, "Journal")
        info_list = buildIt(config.infotxt, "Info")
        todo_list_filtered = helpers.connected_list(todo_list, journal_list, info_list, labels_or_contexts)
        return todo_list_filtered


    # -------------------------------------------------------------------------------------------#

    processChoice(entry)
    # ----------  move up to process choice all below -------------------------------------------#
    if entry == 'options' or entry == 'o':
        option = input("*  rebuild (r)\n"
                       "*  save (s)\n" 
                       "*  dump (d)\n"
                       "*  dumptable (dt)\n\n")
        # -------------------------------------------------------------------------------------------#
        if option == 'rebuild' or option == 'r':  # (if list changed externally)':
            buildIt(config.todotxt, "Todo List")
            writeMenu_main(todo_list)
        # -------------------------------------------------------------------------------------------#
        elif option == 'save' or option == 's':
            log.info('saving (manually triggered')
            save_state(todo_list)
            writeMenu_main(todo_list)
        # -------------------------------------------------------------------------------------------#
        elif option == 'dump' or option == 'd':
            print("\nlenght of list: ", len(todo_list))
            for obj in todo_list:
                print(vars(obj))
            writeMenu_main(todo_list)
        # -------------------------------------------------------------------------------------------#
        elif option == 'dumptable' or option == 'dt':
            print("\nlenght of list: ", len(todo_list))
            table.resultTable(todo_list)
            writeMenu_main(todo_list)
    # -------------------------------------------------------------------------------------------#

    elif entry == 'modify' or entry == 'm':
        updateTodo(todo_list)

    else:
        print("unrecognized input. please try again")
        log.error("user input "+entry+" is invalid")

def writeMenu_list(todo_list):
    global config
    list = input(
        "*  list all (c)ontexts\n"
        "*  list by context (lc)\n"
        "*  list all (l)abels\n"
        "*  list by label (ll)\n"
        "*  list by status (ls)\n"
        "*  list by size (size)\n"
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
        context_dict = helpers.listAllContexts(todo_list)
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
        filtered_list = helpers.listByManualQuery(myQuery,todo_list)
        table.resultTable(filtered_list)
    # -------------------------------------------------------------------------------------------#
    elif list == 'eisenhower' or list == 'e':
        table.eisenhower(todo_list)
    # -------------------------------------------------------------------------------------------#
    elif list == 'labels' or list == 'l':
        log.warning("todolist id is " + str(id(todo_list)))

        helpers.listAllLabels(todo_list,True)
    # -------------------------------------------------------------------------------------------#
    elif list == 'ls context' or list == 'lc':
        context = input('context without @ but accurate cases\n')
        try:
            result = helpers.listByContext(todo_list, journal_list, info_list,context)
            table.resultTable(result)
            print("number of hits:"+str(len(result)))
        except Exception as e:
            print(e)
    # -------------------------------------------------------------------------------------------#
    elif list == 'll' or list == 'ls label':
        label = input('label without +, but accurate cases\n')
        try:
            result = helpers.listByLabel(todo_list, label, journal_list, info_list)
            table.resultTable(result)
        except Exception as e:
            print(e)
    # -------------------------------------------------------------------------------------------#
    elif list == 'size':
        size = input('xs,s,m,l,xl,xxl\n').upper()
        status = input('open or done. or "all"\n')
        if status == "": status = 'open'
        if status == "all": status = ['open','done']
        try:
            result = helpers.listBySize(todo_list,size,status)
            table.resultTable(result)
        except Exception as e:
            print(e)
    # -------------------------------------------------------------------------------------------#
    elif list == "status" or list == 'ls':
        log.debug("running with option list->status (ls)")
        status = input("status. 'open' or 'done'\n")
        log.debug("calling listByStatus(status) with status " + status)
        result = helpers.listByStatus(todo_list, status)
        log.debug("result is set to" + str(len(result)))
        table.resultTable(result)
    # -------------------------------------------------------------------------------------------#
    elif list == "ls prio" or list == 'lp':
        prio = input("a-z\n")
        table.resultTable(helpers.listByPrio(prio.upper(),todo_list))
    # -------------------------------------------------------------------------------------------#
    elif list == "urgency" or list == 'u':
        urgency = input("1-3\n")
        table.resultTable(helpers.listByUrgency(todo_list,urgency))
    # -------------------------------------------------------------------------------------------#
    elif list.startswith("r"):
        log.debug('chose resolved within days')
        try:
            days = int(list.split(" ")[1])
        except IndexError:
            log.warning('invalid input, setting to 0 (today)')
            days = 0
        # the old, static way of building a table
        try:
            # testing building the same with tableobj
            table_content = resolvedWithinDays(days,todo_list)
            table_content = helpers.sortTodos(table_content,"finishDate","urgency","priority")

            resolved_table = Classes.TableObj()
            resolved_table.width = 300
            resolved_table.numOfCols = 9
            resolved_table.colHeaders = ["ID", "P", "U", "Created", "Resolved", "Description", "Context", "Tags", "Size"]
            propertiesToExtract = ["ID", "priority", "urgency", "createDate", "finishDate", "description", "contexts",
                                   "projects", "size"]

            resolved_table.content = helpers.buildListOfListsWithTodoProperties(table_content, propertiesToExtract, resolved_table.descriptionLimiter)
            table.tableFromTableObj(resolved_table, True)

            log.info('done. returning to menu')
        except Exception as e:
            print("unknown Exception caught: ",e)
    # -------------------------------------------------------------------------------------------#

    elif list.startswith("a"):
        # todo simplify and merge with resolved
        log.debug('chose added within days')
        try:
            days = int(list.split(" ")[1])
        except IndexError:
            log.warning('invalid input, setting to 0 (today)')
            days = 0

        # testing building the same with tableobj
        table_content = addedWithinDays(days,todo_list)
        table_content = helpers.sortTodos(table_content,"createDate","urgency","priority")

        added_table = Classes.TableObj()
        added_table.width = 300
        added_table.numOfCols = 9
        added_table.colHeaders = ["ID", "P", "U", "Created", "Resolved", "Description", "Context", "Tags", "Size"]
        propertiesToExtract = ["ID", "priority", "urgency", "createDate", "finishDate", "description", "contexts",
                               "projects", "size"]

        added_table.content = helpers.buildListOfListsWithTodoProperties(table_content, propertiesToExtract, added_table.descriptionLimiter)
        table.tableFromTableObj(added_table, True)

        log.info('done. returning to menu')

def buildIt(filepath, source):
    global config
    log.info("in function 'buildIt(), generating from "+filepath +" and source "+source )
    #open todo file and generate objects and put them into list
    with open(filepath, "r", encoding='UTF-8') as file:
        lines = file.readlines()
    todo_list = []
    Todo.todoCount = 0
    for item in lines:
        try:
            newTodo = Todo(item)
            todo_list.append(newTodo)
        except Exception as e:
            pass
    print(source, " built. Total number of items: %d" % len(todo_list))
    return todo_list

def main():
    #global config
    log.debug("in function main")
    log.info("starting threading")
    # now threading1 runs regardless of user input
    threading1 = threading.Thread(target=background)
    threading1.daemon = True
    threading1.start()
    log.info("reading todo.txt")
    todo_list = buildIt(config.todotxt, "Todo List")

    while True:
        log.debug("writing menu")
        writeMenu_main(todo_list)


if __name__ == "__main__":

    format_string = '%(asctime)s: %(levelname)s: %(message)s'

    log.basicConfig(filename='debug.log', level=log.INFO, format=format_string)
    log.info("---------------- starting ----------------")

    log.warning("TODO: nothing")
    journal_list = []
    log.debug("empty journal_list global var created")
    info_list = []
    log.debug("empty info_list global var created")
    log.debug("now calling main()")
    main()


