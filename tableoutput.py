import text2table
import Classes
import logging as log

config = Classes.Config()


def tableFromTableObj(tableObj, draw = True):
    table = text2table.Texttable(tableObj.width)
    table.add_row(tableObj.colHeaders)
    if type(tableObj.content) == dict:
        for item in tableObj.content.items():
            table.add_row(item)
    else:
        for line in tableObj.content:
            table.add_row(line)
    if draw:
        print(table.draw())
    else:
        return table

def sampleTable():
    table = text2table.Texttable(40)
    table.set_cols_align(["l", "r", "c"])
    table.set_cols_valign(["t", "t", "t"])
    table.add_rows([["Name", "Age", "Nickname"],["Mr Xavier Huon this is a very long name", 32, "Xav'"], ["Mr Baptiste Clement", 1, "Baby"],["Mme Louise Bourgeau", 28, "Lou\n\nLoue"]])
    print(table.draw() + "\n")

def resultTable(result_todo_list,limiter=100,returnTable = False, width=0):
    log.info("in function resultTable()")
    log.info("todo_list holds " + str(len(result_todo_list)) + " items")
    log.info("limiter to restrict description length is set to: " + str(limiter))
    log.info("softwrap (parameter 'width') is set to "+str(width))
    try:
        limiter = limiter
        table = text2table.Texttable(width)
        table.set_cols_align(["l", "l","l","l","l","l", "l","l","l","l"])
        #header
        table.add_row(["ID","Prio","Urgency","Created","Status","Description", "Context", "Tags","Size","Due"])

        for todo in result_todo_list:
            # separate try-catch for contexts and tags, otherwise if one of both is empty, both are set to ""
            try:
                contexts = ", ".join([cntxt for cntxt in todo.contexts])
            except Exception as e:
                contexts = ""
            try:
                tags = ", ".join([tag for tag in todo.projects])
            except:
                tags = ""
            log.debug("row assembled. go on")
            table.add_row([todo.ID,todo.priority,todo.urgency,todo.createDate,todo.status, todo.description[0:limiter].strip(), contexts, tags, todo.size,todo.dueDate])
        if returnTable == False:
            log.info("drawing table because returnTable is False")
            print(table.draw())
        else:
            log.info("in resultTable(), returning table obj because returnTable is True")
            return table
    except Exception as e:
        log.error("drawing table did fail with item")
        print("Uh-oh, something went terribly wrong while drawing the table: \n",e)

def exportThis(result):
    log.debug("in tableoutput.py, function exportThis()")
    table = resultTable(result,10000,True)
    path = config.exports
    filename = input("exporting to: %s \nenter file name\n" % path)
    with open("".join([path,filename]),"w") as out:
        log.info("WWWWWW exporting to: %s %s" % (path,filename))
        for line in table._rows:
            try:
                out.write(";".join(line)+"\n")
            except Exception as e:
                log.critical("was not able to write the following line:")
                log.critical(line)
                log.critical("due to exception:")
                log.critical(e)
        log.info("export done")



def eisenhower(todo_list,testing=False):
    def buildRow(prio, urgency):
        return "\n".join([str(todo.ID)+" - "+todo.description[0:limiter].strip() for todo in todo_list if todo.priority in prio and todo.urgency == urgency and todo.status == "open"])
    log.info("drawing eisenhower list")
    #3x3 Eisenhower list
    limiter = 60
    width = 0
    table = text2table.Texttable(width)
    log.info("limiting description lenght to "+str(limiter)+" characters to keep table to span multiple screens")
    log.info("softwrap (table width is set to "+str(width))
    table.add_row([""       ,"Low Urgency","Medium Urgency","High Urgency", "Escalation & Interruptive"])

    log.debug("drawing row (A)")
    prio_list = ["(" + char + ")" for char in "a".upper()]
    A_low = buildRow(prio_list,"3")
    A_med = buildRow(prio_list,"2")
    A_hig = buildRow(prio_list,"1")
    A_esc = buildRow(prio_list,"0")
    table.add_row(["(A)", A_low, A_med, A_hig, A_esc])

    log.debug("drawing row (B)&(C)")
    prio_list = ["(" + char + ")" for char in "bc".upper()]
    B_low = buildRow(prio_list,"3")
    B_med = buildRow(prio_list,"2")
    B_hig = buildRow(prio_list,"1")
    B_esc = buildRow(prio_list,"0")
    table.add_row(["(B)&(C)", B_low, B_med, B_hig, B_esc])

    log.debug("drawing row (D)-(G)")
    prio_list = ["(" + char + ")" for char in "defg".upper()]
    DG_low = buildRow(prio_list,"3")
    DG_med = buildRow(prio_list,"2")
    DG_hig = buildRow(prio_list,"1")
    DG_esc = buildRow(prio_list,"0")
    table.add_row(["(D)-(G)", DG_low, DG_med, DG_hig, DG_esc])

    prio_list = ["("+ char +")"for char in "hijklmnopqrstuvwxyz".upper()]
    HZ_low = buildRow(prio_list,"3")
    HZ_med = buildRow(prio_list,"2")
    HZ_hig = buildRow(prio_list,"1")
    HZ_esc = buildRow(prio_list,"0")
    table.add_row(["(H)-(Z)", HZ_low, HZ_med, HZ_hig, HZ_esc])

    if not testing:
        print(table.draw())
    else:
        return table

def labelTable(allLabels, drawtable = True):
    allTables = []
    cols_width = 30
    ABCDEF_table = text2table.Texttable(0)
    ABCDEF_table.set_cols_width([cols_width,cols_width,cols_width,cols_width,cols_width,cols_width])
    ABCDEF_table.add_row([char for char in "ABCDEF"])
    a= "\n".join([l for l in allLabels if l.startswith("+a") or l.startswith("+A")])
    b= "\n".join([l for l in allLabels if l.startswith("+b") or l.startswith("+B")])
    c= "\n".join([l for l in allLabels if l.startswith("+c") or l.startswith("+C")])
    d= "\n".join([l for l in allLabels if l.startswith("+d") or l.startswith("+D")])
    e= "\n".join([l for l in allLabels if l.startswith("+e") or l.startswith("+E")])
    f= "\n".join([l for l in allLabels if l.startswith("+f") or l.startswith("+F")])
    ABCDEF_table.add_row([a,b,c,d,e,f])
    allTables.append(ABCDEF_table)
    GHIJKL_table = text2table.Texttable(0)
    GHIJKL_table.set_cols_width([cols_width,cols_width,cols_width,cols_width,cols_width,cols_width])
    GHIJKL_table.add_row([char for char in "GHIJKL"])
    g = "\n".join([l for l in allLabels if l.startswith("+g") or l.startswith("+G")])
    h = "\n".join([l for l in allLabels if l.startswith("+h") or l.startswith("+H")])
    i = "\n".join([l for l in allLabels if l.startswith("+i") or l.startswith("+I")])
    j = "\n".join([l for l in allLabels if l.startswith("+j") or l.startswith("+J")])
    k = "\n".join([l for l in allLabels if l.startswith("+k") or l.startswith("+K")])
    l = "\n".join([l for l in allLabels if l.startswith("+l") or l.startswith("+L")])
    GHIJKL_table.add_row([g,h,i,j,k,l])
    allTables.append(GHIJKL_table)
    MNOPQR_table = text2table.Texttable(0)
    MNOPQR_table.set_cols_width([cols_width,cols_width,cols_width,cols_width,cols_width,cols_width])
    MNOPQR_table.add_row([char for char in "MNOPQR"])
    m = "\n".join([l for l in allLabels if l.startswith("+m") or l.startswith("+M")])
    n = "\n".join([l for l in allLabels if l.startswith("+n") or l.startswith("+N")])
    o = "\n".join([l for l in allLabels if l.startswith("+o") or l.startswith("+O")])
    p = "\n".join([l for l in allLabels if l.startswith("+p") or l.startswith("+P")])
    q = "\n".join([l for l in allLabels if l.startswith("+q") or l.startswith("+Q")])
    r = "\n".join([l for l in allLabels if l.startswith("+r") or l.startswith("+R")])
    MNOPQR_table.add_row([m,n,o,p,q,r])
    allTables.append(MNOPQR_table)
    STUVWX_table = text2table.Texttable(0)
    STUVWX_table.set_cols_width([cols_width,cols_width,cols_width,cols_width,cols_width,cols_width])
    STUVWX_table.add_row([char for char in "STUVWX"])
    s = "\n".join([l for l in allLabels if l.startswith("+s") or l.startswith("+S")])
    t = "\n".join([l for l in allLabels if l.startswith("+t") or l.startswith("+T")])
    u = "\n".join([l for l in allLabels if l.startswith("+u") or l.startswith("+U")])
    v = "\n".join([l for l in allLabels if l.startswith("+v") or l.startswith("+V")])
    w = "\n".join([l for l in allLabels if l.startswith("+w") or l.startswith("+W")])
    x = "\n".join([l for l in allLabels if l.startswith("+x") or l.startswith("+X")])
    STUVWX_table.add_row([s,t,u,v,w,x])
    allTables.append(STUVWX_table)
    YZ_table = text2table.Texttable(0)
    YZ_table.set_cols_width([cols_width,cols_width])
    YZ_table.add_row([char for char in "YZ"])
    y = "\n".join([l for l in allLabels if l.startswith("+y") or l.startswith("+Y")])
    z = "\n".join([l for l in allLabels if l.startswith("+z") or l.startswith("+Z")])
    YZ_table.add_row([y,z])
    allTables.append(YZ_table)
    if drawtable:
        for table in allTables:
            print(table.draw())
    else:
        return allTables
