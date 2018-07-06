class NoInputFilesError(Exception):
    def __init__(self, spec_path):
        self.spec_path = spec_path

    def __str__(self):
        return repr(self.spec_path) + " has no input_file fields"

class UnknownGenerator(Exception):
    def __init__(self, generator):
        self.generator = generator

    def __str__(self):
        return repr(self.generator) + " is not recognized"