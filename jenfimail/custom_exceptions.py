class LineNotValidException(Exception):
    def __init__(self):
        self.message = 'line not valid'
        super().__init__(self.message)

class LineNotAvailableException(Exception):
    def __init__(self):
        self.message = 'line not available'
        super().__init__(self.message)
