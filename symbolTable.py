class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.method_table = {}
        self.reset_table = {}
        self.indexes = {"static": 0, "field": 0, "arg": 0, "var": 0} # Keep counters for each kind

    def reset(self):
        """
        The function operates on an existing method table and empties it
        """
        self.method_table.clear()
        self.indexes["arg"] = 0
        self.indexes["var"] = 0

    def define(self, name, type, kind):
        """
        :param name: the name of symbol in table
        :param type: type of it (given types such as int, String or created types such as "pointer")
        :param kind: one of the group - static, field, arg or var
        Adds the arguments to the relevant table
        """
        idx = self.indexes[kind]
        entry = {"type": type, "kind": kind, "index": idx}
        if kind in ("static", "field"):
            self.class_table[name] = entry
        else:
            self.method_table[name] = entry
        self.indexes[kind] += 1

    def varCount(self, kind):
        """
        :param kind
        :return - number of variables of a given kind already in the table
        """
        return self.indexes[type]

    def kindOf(self, name):
        """
        :param name
        :return - first searches in the current method for the kind, else in the class scope, otherwise returns None
        """
        if name in self.method_table:
            return self.method_table[name]["kind"]
        elif name in self.class_table:
            return self.class_table[name]["kind"]
        return None

    def typeOf(self, name):
        """
        :param name
        :return - - first searches in the current method for the type, else in the class scope, otherwise returns None
        """
        if name in self.method_table:
            return self.method_table[name]["type"]
        elif name in self.class_table:
            return self.class_table[name]["type"]
        return None

    def indexOf(self, name):
        """
              :param name
              :return - - first searches in the current method for the index, else in the class scope, otherwise returns None
              """
        if name in self.method_table:
            return self.method_table[name]["index"]
        elif name in self.class_table:
            return self.class_table[name]["index"]
        return None





