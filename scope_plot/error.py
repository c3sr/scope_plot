class NoInputFilesError(Exception):
    def __init__(self, spec_path):
        self.spec_path = spec_path

    def __str__(self):
        return repr(self.spec_path) + " has no input_file fields"


class NoBackendError(Exception):
    """raise when a spec file does not define 'backend'"""
    def __str__(self):
        return "spec did not define 'backend'"


class UnknownGenerator(Exception):
    def __init__(self, generator):
        self.generator = generator

    def __str__(self):
        return repr(self.generator) + " is not recognized"
