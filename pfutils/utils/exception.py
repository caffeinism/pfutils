class ParseError(Exception):
    def __init__(self, data, type):
        self.data = data
        self.type = type
        
        super().__init__(f'"{data}" does not match as {type}.')

class PortError(Exception):
    def __init__(self, port):
        self.port = port
        
        super().__init__(f'The port must be less than or equal to 65535.')
        
class NotFoundError(Exception):
    def __init__(self):
        super().__init__(f'Cannot found resources.')
        
class AlreadyExistError(Exception):
    pass