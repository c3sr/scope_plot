import json
import re
import copy

import pandas as pd

class ContextMismatchError(Exception):
    def __init__(self, field):
        super(ContextMismatchError, self).__init__("field {} mismatched".format(field))

class GoogleBenchmark(object):
    def __init__(self, path=None, stream=None):
        self.context = {}
        self.benchmarks = []
        if path:
            with open(path, "rb") as f:
                j = json.loads(f.read().decode("utf-8"))
            self.context = j["context"]
            self.benchmarks = j["benchmarks"]
        elif stream:
            j = json.loads(stream.read().decode("utf-8"))
            self.context = j["context"]
            self.benchmarks = j["benchmarks"]
    
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def filter_name(self, regex):
        filtered = copy.deepcopy(self)
        pattern = re.compile(regex)
        filtered.benchmarks = [b for b in filtered.benchmarks if pattern.search(b["name"])]
        return filtered

    def filter_field(self, field_name):
        self.filter_fields(field_name)

    def filter_fields(self, *field_names):
        """filter out benchmarks missing any field in field_names"""
        filtered = copy.deepcopy(self)
        def allow(b):
            for name in field_names:
                if name not in b:
                    return False
            return True
        filtered.benchmarks = list(filter(allow, filtered.benchmarks))

    def json(self):
        return json.dumps(
            {
                "context": self.context,
                "benchmarks": self.benchmarks,
            },
            indent=4
        )

    def fields(self, *field_names):
        """for each field_name, return a list corresponding to that """
        def show_func(b):
            for name in field_names:
                if name not in b:
                    return False
            if "error_message" in b:
                return False
            return True
        data = []
        for name in field_names:
            data += [list(map(lambda b: float(b[name]), filter(show_func, self.benchmarks)))]
        return tuple(data)

    def xy_dataframe(self, x_field, y_field):
        """produce a pandas dataframe indexed by x_field with a column for y_field"""
        def valid_func(b):
            if "error_message" in b or x_field not in b or y_field not in b:
                return False
            return True
        data = {}
        data[x_field] = list(map(lambda b: float(b[x_field]), filter(valid_func, self.benchmarks)))
        data[y_field] = list(map(lambda b: float(b[y_field]), filter(valid_func, self.benchmarks)))

        df = pd.DataFrame.from_dict(data)
        df = df.set_index(x_field)
        return df

    def custom_dataframe(self, index, *columns):
        """return a pandas dataframe indexed by 'index' with column names 'columns'"""
        raise NotImplementedError

    def dataframe(self):
        """return a pandas dataframe containing a row for each benchmark entry"""

        def make_frame(b):
            return pd.DataFrame(b)

        frames = [make_frame(b) for b in self.benchmarks]
        return pd.concat(frames)

    def __iadd__(self, other):
        """add other benchmarks into self, without checking context"""
        return self.merge_into(other, ignore_context=True)

    def merge_into(self, other, ignore_context=True):
        """add benchmarks from other into self. if ignore_context=True, do not check context for consistency"""
        if not self.context:
            self.context = other.context

        if not ignore_context:
            def context_equal_or_raise(field):
                if self.context[field] != other.context[field]:
                    raise ContextMismatchError(field)
            context_equal_or_raise("num_cpus")
            context_equal_or_raise("library_build_type")
            context_equal_or_raise("caches")
            context_equal_or_raise("cpu_scaling_enabled")

        self.benchmarks += other.benchmarks
        
        return self