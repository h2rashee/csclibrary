import abc

class LibrarianException(Exception, metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def error_msg(self):
        pass

    def __str__(self):
        return self.error_msg

class PermissionsError(LibrarianException):
    def __init__(self, permission_string):
        self.permission_string = permission_string

    @property
    def error_msg(self):
        return "Need privilege level {}".format(self.permission_string)
