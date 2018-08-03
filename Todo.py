import re
import logging as log
# need to do it properly. put getters and setters. setters will update the property AND the rawline
class Todo:
    todoCount = 0

    def __init__(self, rawLine):
        self.ID = Todo.todoCount
        self.rawline = self.setRawLine(rawLine)
        self.priority = self.setPrio(rawLine)
        self.urgency = self.setUrgency(rawLine)
        self.status = self.setStatus(rawLine)
        self.createDate = self.setCreateDate(rawLine)
        self.finishDate = self.setFinishDate(rawLine)
        self.dueDate = self.setDueDate(rawLine)
        self.description = self.setDescription(rawLine)
        self.contexts = self.setContexts(rawLine)
        self.projects = self.setProjects(rawLine)
        self.size = self.setSize(rawLine)
        self.recurring = self.setRecurring(rawLine)
        Todo.todoCount += 1

    def __del__(self):
        #print("destrucor called, deleting object")
        pass

    def setRawLine(self,rl):
        return rl

    def updateRawline(self,prprty,value):
        log.info("updating raw line with regex "+str(prprty))
        # find element by regex and replace
        # if not found, append to rawline
        # expects prprty being the correct regex
        regex = prprty
        try:

            found = re.search(prprty, self.rawline).group()
            self.rawline = re.sub(regex,value,self.rawline)
        except:
            log.info("no match found for regex "+ regex)
            log.info("appending to raw line instead")
            log.info("before "+self.rawline)
            self.rawline = (self.rawline+" "+value).replace("\n","")
            log.info("after "+self.rawline)



    def setPrio(self, rl):
        regex = r"\([A-Z]\)"
        try:
            return re.search(regex, rl).group()
        except Exception as e:
            return "( )" #keine prio gesetzt. auch ok

    def setUrgency(self, rl):
        regex = r"\{[0-3]\}"
        try:
            urgency = re.search(regex, rl).group()
            urgency = urgency.replace("{","")
            urgency = urgency.replace("}", "")
            return urgency
        except Exception as e:
            return "( )" #keine prio gesetzt. auch ok
    def setStatus(self,rl):
        regex = r"^x\s\d\d\d\d-\d\d-\d\d" #maybe the date is overkill, or stuff gets done without a done-date. revisit later. also in respect of the finish-date
        if re.search(regex, rl):
            return "done"
        else:
            return 'open'
    def setCreateDate(self, rl):
        #find a \d\d\d\d-\d\d-\d\d pattern without '^x\s' in front. oder von hinten aufrollen, nachdem das optional due: date übersprungen wurde
        regex_finishDate = r"(^x\s)(\d\d\d\d-\d\d\-\d\d)"
        regex_dueDate = r"due\:\d\d\d\d-\d\d-\d\d"
        rl = re.sub(regex_finishDate, "", rl)
        rl = re.sub(regex_dueDate,"",rl)
        regex = r"\d{4}-\d{2}-\d{2}"
        if re.search(regex, rl):
            #converting date string to real date (03.08.18)
            datestring = re.search(regex, rl).group().strip()
            #realdate = datetime.date(int(datestring.split('-')[0]), int(datestring.split('-')[1]), int(datestring.split('-')[2]))
            return re.search(regex, rl).group().strip()
        pass
    def setFinishDate(self,rl):
        regex = r"(^x\s)(\d\d\d\d-\d\d\-\d\d)"
        if re.search(regex, rl):
            try:
                return re.search(regex,rl).group(2)
            except Exception as e:
                print(e)
        else:
            pass
    def setDueDate(self, rl):
        regex = r"due\:\s?\d\d\d\d-\d\d-\d\d"
        if re.search(regex, rl):
            dueDate_string = re.search(regex, rl).group()
            return dueDate_string.split(":")[1]
        else:
            pass
    def setDescription(self, rl):
        try:
            dates_regex = re.compile(r"\d\d\d\d-\d\d-\d\d")
            due_regex = re.compile(r"due\:")
            status_regex = re.compile(r"\([A-Z]\)")
            size_regex = re.compile(r"\$\$([a-zA-Z]*)")
            stripx_regex = re.compile(r"^x\s*")
            urgency_regex = re.compile(r"\{[0-3]\}")
            rl = re.sub(status_regex, "", rl)
            rl = re.sub(dates_regex,"",rl)
            rl = re.sub(due_regex,"",rl)
            rl = re.sub(stripx_regex,"",rl)
            rl = re.sub(size_regex,"",rl)
            rl = re.sub(urgency_regex,"",rl)
            return rl.strip()
        except Exception as e:
            print(e)
            return "No Description found"


    def setContexts(self, rl):
        regex = r"\s(@[a-zA-Z0-9]*)"
        if re.search(regex, rl):
            all_contexts_list = re.findall(regex, rl)
            # stripping all whitespaces from contexts with list comprehension
            all_contexts_list = [c.replace(c,c.strip()) for c in all_contexts_list]
            return all_contexts_list
        else:
            pass
    def setProjects(self, rl):
        regex = r"\s\+[a-zA-Z0-9]+"
        if re.search(regex, rl):
            #stripping whitespace from all labels with list comprehension
            all_labels_list = re.findall(regex, rl)
            all_labels_list = [l.replace(l,l.strip()) for l in all_labels_list]
            return all_labels_list
        else:
            pass
    def setSize(self, rl):
        regex = r"\$\$([a-zA-Z]*)"
        if re.search(regex, rl):
            #return re.findall(regex, rl).upper()
            return re.search(regex, rl).group().replace("$$","").upper()
        else:
            pass
    def setRecurring(self, rl):
        regex = r"\s\<(yes|no)\>"
        if re.search(regex, rl):
            #return re.findall(regex, rl).upper()
            return re.search(regex, rl).group()
        else:
            pass

