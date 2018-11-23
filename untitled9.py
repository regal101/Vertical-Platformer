import pytmx

class f:
    def __init__(self,filename):
        tm = pytmx.load_pygame(filename,pixelalpha=True)
