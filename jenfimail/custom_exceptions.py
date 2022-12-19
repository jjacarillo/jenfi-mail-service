class LineNotValidException(Exception):
    def __init__(self):
        self.message = 'line not valid'
        super().__init__(self.message)

class LineNotAvailableException(Exception):
    def __init__(self):
        self.message = 'line not available'
        super().__init__(self.message)

class LinesNotFoundException(Exception):
    def __init__(self):
        self.message = 'line not found'
        super().__init__(self.message)

class NoParcelsToLoadException(Exception):
    def __init__(self):
        self.message = 'no parcels to load'
        super().__init__(self.message)

class FailedToLoadParcelsException(Exception):
    def __init__(self):
        self.message = 'failed to load parcels'
        super().__init__(self.message)

class ParcelNotPendingException(Exception):
    def __init__(self):
        self.message = 'unable to withdraw parcel not in pending state'
        super().__init__(self.message)
