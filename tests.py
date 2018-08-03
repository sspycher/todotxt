import unittest
from tdt import *
import helpers
import Todo
import tableoutput
import Classes


class TdtTest(unittest.TestCase):

    def setUp(self):
        global todo_list
        rawTodo1 = "(A) 2021-01-01 this is a dummy todo following the proposed structure {1} +WTF . and now i'm adding a whole lot of more text to be able to teest lenght assertions later on (182 chars)"
        rawTodo2 = "(B) 2019-01-02 01-01-2020 and this one is a fucking mess {2}1 +testing and this @Context"
        rawTodo3 = "(Z) 2022-01-03 -11-11 this is a + sign that should not be added to label list. neither should email@adresses.com, @Testing"
        todo_list.append(Todo.Todo(rawTodo1))
        todo_list.append(Todo.Todo(rawTodo2))
        todo_list.append(Todo.Todo(rawTodo3))




    def tearDown(self):
        global todo_list
        try:
            todo_list=[]
        except Exception as e:
            print("did not delete anything due to",e)

    def test_listAllLabelsLength(self):
        global todo_list
        myVal = listAllLabels(todo_list,False)
        self.assertEqual(len(myVal),2)

    def test_listAllContextsLength(self):
        global todo_list
        myVal = listAllContexts(todo_list)
        self.assertEqual(len(myVal),2)

    def test_labelsStartWithPlus(self):
        global todo_list
        extractedLabels = listAllLabels(todo_list, False)
        for string in extractedLabels:
            self.assertEqual(string[0:1],"+")


    def test_listAllLabelsObjTypes(self):
        global todo_list
        label_list = ["+label1","+label2"]
        tables = labelTable(label_list, False)
        self.assertIsInstance(tables,list)
        for table in tables:
            self.assertIsInstance(table,text2table.Texttable)

    def test_listByLabel(self):
        #global todo_list
        result = listByLabel(todo_list, "WTF")
        self.assertEqual(result[0].projects[0],'+WTF')

    def test_buildConnectionTable(self):
        journal = ['2018-01-01 this is a journal entry with +WTF as label and @Testing as context','2018-01-01 this is a journal entry with +WTFF as label and @NotTesting as context']
        journal_list = []
        for entry in journal:
            new_obj = Todo.Todo(entry)
            journal_list.append(new_obj)
        info = ['2018-01-01 this is a info entry with +WTF as label and @Testing as context','2018-01-01 this is a info entry with +WTFF as label and @NotTesting as context']
        info_list = []
        for entry in info:
            new_obj = Todo.Todo(entry)
            info_list.append(new_obj)

        # fetch all todos with context Testing
        result_context = listByContext(todo_list, "Testing")
        # connect those todos with content from info and journal
        # must have 3 elements
        connected_contexts = helpers.buildConnectionTable(result_context, "@Testing", journal_list, info_list)
        self.assertEqual(len(connected_contexts),3)

        # fetch all todos with label WTF
        result_label = listByLabel(todo_list, "WTF")
        # connect / enrich those todos with content from info and journal
        connected_labels = helpers.buildConnectionTable(result_label, "+WTF", journal_list, info_list)
        self.assertEqual(len(connected_labels),3)

    def test_CSVExport(self):
        pass


    def test_buildListOfListsWithTodoProperties(self):
        propertiesToExtract = ["ID", "priority", "urgency", "createDate", "finishDate", "description", "contexts",
                               "projects", "size"]
        descriptionLimiter = 20
        result = helpers.buildListOfListsWithTodoProperties(todo_list, propertiesToExtract, descriptionLimiter)
        self.assertIsInstance(result,list,"is list")
        self.assertIsInstance(result[0],list)
        self.assertTrue(len(result)==3)
        self.assertTrue(len(result[0]) == len(propertiesToExtract))
        self.assertTrue(len(result[0][5]) <= descriptionLimiter)
        # testing with unmatching numbers of properties (-1)
        propertiesToExtract = ["ID", "priority", "urgency", "createDate", "finishDate", "description", "contexts",
                               "projects"]
        result = helpers.buildListOfListsWithTodoProperties(todo_list, propertiesToExtract, descriptionLimiter)
        self.assertRaises(AttributeError)

    def test_createTableByTableObj(self):
        tableObj = Classes.TableObj()
        tableObj.descriptionLimiter = 100
        tableObj.colHeaders = ["Col1","Col2"]
        tableObj.content = [["content col 1","content col2"]]
        tableObj.numOfCols = 2
        tableObj.width = 0
        resultTable = tableoutput.tableFromTableObj(tableObj,False)
        self.assertEqual(resultTable._rows[0][0],"Col1")
        self.assertEqual(resultTable._rows[1][1],"content col2")

    def test_sortingTodosByProperies(self):
        sorted_list = helpers.sortTodos(todo_list,'createDate')
        def createDatefromString(datestring):
            dateList = datestring.split("-")
            return datetime.date(int(dateList[0]), int(dateList[1]), int(dateList[2]))
        date1 = createDatefromString(sorted_list[0].createDate)
        date2 = createDatefromString(sorted_list[1].createDate)
        date3 = createDatefromString(sorted_list[2].createDate)
        print(date1,date2,date3)
        self.assertTrue(date1 < date2 < date3)
if __name__ == "__main__":
    todo_list = []
    unittest.main()