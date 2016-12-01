class Loader(object):

    def loadFromFile(self, file_name):
        file = open(file_name, 'r')
        content = file.read()
        content_array = content.split('\n')
        return content_array

    def loadUData(self):
        content_array = self.loadFromFile('../u2.data')
        content_array_toreturn = []

        for elem in content_array:
            row = elem.split("\t")
            if len(row) > 1:
                content_array_toreturn.append(row)

        return content_array_toreturn

    def loadUUser(self):
        content_array = self.loadFromFile('../u.user')
        content_array_toreturn = []

        for elem in content_array:
            row = elem.split("|")
            if len(row) > 1:
                content_array_toreturn.append(row)

        return content_array_toreturn
