from apiflask import APIFlask

class Djask(APIFlask):
    def __init__(self, *args, **kwargs):
        super(self).__init__(*args, **kwargs)
