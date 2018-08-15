import unittest
from tdt import *
import helpers
import Todo
import tableoutput as table
import Classes
import text2table


class TdtTest(unittest.TestCase):

    def setUp(self):
        global todo_list
        rawTodo1 = "(A) 2021-01-01 this is a dummy todo following the proposed structure {1} +WTF . and now i'm adding a whole lot of more text to be able to teest lenght assertions later on (182 chars)"
        rawTodo2 = "(B) 2019-01-02 01-01-2020 and this one is a fucking mess {2}1 +testing and this @Context"
        rawTodo3 = "(Z) 2022-01-03 this is a + sign that should not be added to label list. {3} neither should email@adresses.com, @Testing"
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
        myVal = helpers.listAllLabels(todo_list,False)
        self.assertEqual(len(myVal),2)

    def test_listAllContextsLength(self):
        global todo_list
        myVal = helpers.listAllContexts(todo_list)
        self.assertEqual(len(myVal),2)

    def test_labelsStartWithPlus(self):
        global todo_list
        extractedLabels = helpers.listAllLabels(todo_list, False)
        for string in extractedLabels:
            self.assertEqual(string[0:1],"+")

    def test_listAllLabelsObjTypes(self):
        global todo_list
        label_list = ["+label1","+label2"]
        tables = helpers.labelTable(label_list, False)
        self.assertIsInstance(tables,list)
        for table in tables:
            self.assertIsInstance(table,text2table.Texttable)

    def test_listByLabel(self):
        #global todo_list
        result = helpers.listByLabel(todo_list, "WTF")
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
        result_context = helpers.listByContext(todo_list, "Testing")
        # connect those todos with content from info and journal
        # must have 3 elements
        connected_contexts = helpers.buildConnectionTable(result_context, "@Testing", journal_list, info_list)
        self.assertEqual(len(connected_contexts),3)

        # fetch all todos with label WTF
        result_label = helpers.listByLabel(todo_list, "WTF")
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
        resultTable = helpers.tableoutput.tableFromTableObj(tableObj,False)
        self.assertEqual(resultTable._rows[0][0],"Col1")
        self.assertEqual(resultTable._rows[1][1],"content col2")

    def test_sortingTodosByProperies(self):
        # recreating todos to make the sorting more relevant
        todo_list = []
        todo_list.append(Todo.Todo("(C) 2018-08-01 {0} this has urgency zero $$s"))
        todo_list.append(Todo.Todo("(A) 2018-08-01 {0} this has urgency zero $$xs"))
        todo_list.append(Todo.Todo("(A) 2018-09-01 {1} this has urgency one $$m"))
        todo_list.append(Todo.Todo("(A) 2018-08-01 {2} this has urgency two $$xl"))
        todo_list.append(Todo.Todo("(B) 2018-07-01 {2} this has urgency two $$xxl"))
        todo_list.append(Todo.Todo("(A) 2018-07-01 {2} this has urgency two $$l"))

        """
        sorting by (order) urgency, prio, createDate must yield
        
        (A) 2018-08-01 {0} this has urgency zero $$xs
        (C) 2018-08-01 {0} this has urgency zero $$s
        (A) 2018-09-01 {1} this has urgency one $$m
        (A) 2018-07-01 {2} this has urgency two $$l
        (A) 2018-08-01 {2} this has urgency two $$xl
        (B) 2018-07-01 {2} this has urgency two $$xxl
        
        to check, i'm abusing the size property (xs-xxl)
        """
        # this is the 'natural' way of prioritising the sort order. must be reversed in the function sortTodos
        sorted_list = helpers.sortTodos(todo_list,'urgency','priority','createDate')
        sorted_sizes = []
        for todo in sorted_list:
            sorted_sizes.append(todo.size)
        self.assertListEqual(sorted_sizes,["XS","S","M","L","XL","XXL"])

    def test_datesaredatesinTodo(self):
        todo_list.append(Todo.Todo("x 2018-01-01 (C) 2018-08-01 {0} this has urgency zero $$s due:2020-01-01"))

        self.assertIsInstance(getattr(todo_list[3],'createDate'), datetime.date)
        self.assertIsInstance(getattr(todo_list[3], 'finishDate'), datetime.date)
        self.assertIsInstance(getattr(todo_list[3], 'dueDate'), datetime.date)

    def test_resolvedWithinDays(self):
        resolvedDate1 = datetime.date.today() - datetime.timedelta(3)
        resolvedDate2 = datetime.date.today() - datetime.timedelta(4)

        todo_list.append(Todo.Todo("x "+str(resolvedDate1)+" (C) 2018-08-01 {0} this has urgency zero $$s due:2020-01-01"))
        todo_list.append(Todo.Todo("x "+str(resolvedDate2)+" (C) 2018-08-01 {0} this has urgency zero $$s due:2020-01-01"))

        resolved_todos = resolvedWithinDays(1, todo_list)
        self.assertEqual(len(resolved_todos),0)

        resolved_todos = resolvedWithinDays(2, todo_list)
        self.assertEqual(len(resolved_todos),0)

        resolved_todos = resolvedWithinDays(3, todo_list)
        self.assertEqual(len(resolved_todos),1)

        resolved_todos = resolvedWithinDays(4, todo_list)
        self.assertEqual(len(resolved_todos),2)

    def test_addedWithinDays(self):
        addedDate1 = datetime.date.today() - datetime.timedelta(3)
        addedDate2 = datetime.date.today() - datetime.timedelta(4)

        todo_list.append(Todo.Todo("(C) "+str(addedDate1)+" {0} this has urgency zero $$s due:2020-01-01"))
        todo_list.append(Todo.Todo("(C) "+str(addedDate2)+" {0} this has urgency zero $$s due:2020-01-01"))

        added_todos = addedWithinDays(1, todo_list)
        self.assertEqual(len(added_todos),0)

        added_todos = addedWithinDays(2, todo_list)
        self.assertEqual(len(added_todos),0)

        added_todos = addedWithinDays(3, todo_list)
        self.assertEqual(len(added_todos),1)

        added_todos = addedWithinDays(4, todo_list)
        self.assertEqual(len(added_todos),2)

    def test_listCommands(self):
        import tdt
        # resetting and refilling todolist to improve testability

        todo_list.append(Todo.Todo("(A) {0} this is the second @Testing test@mail.com context"))

        # testing contexts
        # ---------------------------------------------------------------
        context_dict = tdt.listAllContexts(todo_list)
        self.assertIsInstance(context_dict,dict)
        self.assertDictEqual(context_dict,{'@Testing': 2, '@Context': 1})
        # testing query u=0 p=a s=o
        # ---------------------------------------------------------------
        myQuery = Classes.Query("u=1 p=a s=o")
        filtered_list = tdt.byManualQuery(myQuery,todo_list)
        self.assertTrue(len(filtered_list),1)
        # eisenhower
        # ---------------------------------------------------------------
        todo_list.append(Todo.Todo("(F) {3} eisenhower this is the second @Testing test@mail.com context"))
        table_obj = tdt.eisenhower(todo_list,True)
        self.assertEqual(table_obj._rows[1][3], " - ".join([str(todo_list[0].ID),todo_list[0].description[0:60].strip()]))
        # list by prio (lp)
        # ---------------------------------------------------------------
        prio = "Z"
        todos_filtered = helpers.listByPrio(prio, todo_list)
        self.assertEqual(todos_filtered[0].priority, "(Z)")
        self.assertEqual(len(todos_filtered),1)

if __name__ == "__main__":
    todo_list = []
    unittest.main()