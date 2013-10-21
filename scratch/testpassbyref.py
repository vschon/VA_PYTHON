class AA():

    def __init__(self):
        self.content = [1,2,3]

class BB():
    def __init__(self,content):
        self.content = content

    def modifyA(self):
        self.content.append(4)

    def printA(self):
        print self.content
