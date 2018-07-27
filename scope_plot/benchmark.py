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

    def keep_name_regex(self, regex):
        """retain benchmarks whose name matches regex"""
        filtered = copy.deepcopy(self)
        pattern = re.compile(regex)
        filtered.benchmarks = [b for b in filtered.benchmarks if pattern.search(b["name"])]
        return filtered

    def keep_name_endswith(self, substr):
        """retain benchmarks whose name ends with substr"""
        filtered = copy.deepcopy(self)
        filtered.benchmarks = [b for b in filtered.benchmarks if b["name"].endswith(substr)]
        return filtered

    def remove_name_endswith(self, substr):
        """remove benchmarks whose name ends with substr"""
        filtered = copy.deepcopy(self)
        filtered.benchmarks = [b for b in filtered.benchmarks if not b["name"].endswith(substr)]
        return filtered

    def keep_field(self, field_name):
        """retain benchmarks with field_name"""
        return self.keep_fields(field_name)

    def keep_fields(self, *field_names):
        """retain benchmarks with all field_names"""
        filtered = copy.deepcopy(self)
        def allow(b):
            for name in field_names:
                if name not in b:
                    return False
            return True
        filtered.benchmarks = list(filter(allow, filtered.benchmarks))
        return filtered

    def keep_stats(self):
        """retain benchmarks that correspond to aggregate stats (mean, median, stddev)"""
        filtered = copy.deepcopy(self)
        filtered.benchmark = []
        for b in self.benchmarks:
            if any(b["name"].endswith(suffix) for suffix in ("_mean", "_median", "_err")):
                filtered.benchmarks += [b]
        return filtered

    def keep_raw(self):
        """retain benchmarks that do not correspond to aggregate stats"""
        return self.remove_name_endswith("_mean") \
                   .remove_name_endswith("_median") \
                   .remove_name_endswith("_stddev")

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

        # both x_field and y_field should be present
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
        """return a pandas dataframe containing a row for each benchmark object"""
        frames = [pd.DataFrame(b, index=[0]) for b in self.benchmarks]
        return pd.concat(frames, ignore_index=True)

    def stats_dataframe(self, x_field, y_field):
        """return a pandas dataframe containing a row corresponding to each benchmark with x_field, y_field for which aggregate stats can be found"""

        stats = {}
        for b in self.benchmarks:

            if x_field not in b or "error_message" in b:
                continue

            name = b["name"]
            if name.endswith("_mean"):
                stats[x_field]["mean"] = b[y_field]
            elif name.endswith("_mediean"):
                stats[x_field]["median"] = b[y_field]
            elif name.endswith("_stddev"):
                stats[x_field]["stddev"] = b[y_field]
            else:
                continue
            
            columns = {"x": [], "mean":[], "median":[], "stddev":[]}
            for x_value in stats:
                columns["x"] += [x_value]

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