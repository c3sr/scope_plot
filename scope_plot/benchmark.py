import json
import re
import copy
from collections import defaultdict

import pandas as pd


class ContextMismatchError(Exception):
    def __init__(self, field):
        super(ContextMismatchError,
              self).__init__("field {} mismatched".format(field))


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
        filtered.benchmarks = [
            b for b in filtered.benchmarks if pattern.search(b["name"])
        ]
        return filtered

    def keep_name_endswith(self, substr):
        """retain benchmarks whose name ends with substr"""
        filtered = copy.deepcopy(self)
        filtered.benchmarks = [
            b for b in filtered.benchmarks if b["name"].endswith(substr)
        ]
        return filtered

    def remove_name_endswith(self, substr):
        """remove benchmarks whose name ends with substr"""
        filtered = copy.deepcopy(self)
        filtered.benchmarks = [
            b for b in filtered.benchmarks if not b["name"].endswith(substr)
        ]
        return filtered

    def keep_field(self, field_name):
        """retain benchmarks with a field matching regex field_name"""
        return self.keep_fields(field_name)

    def keep_fields(self, *field_names):
        """retain benchmarks with fields matching all field_names regexes"""
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
            if any(b["name"].endswith(suffix)
                   for suffix in ("_mean", "_median", "_stddev")):
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
            indent=4)

    def fields(self, *field_names):
        """return a tuple of lists, where each list contains the benchmark data from the field in field_names"""

        def show_func(b):
            for name in field_names:
                if name not in b:
                    return False
            if "error_message" in b:
                return False
            return True

        data = []
        for name in field_names:
            data += [
                list(
                    map(lambda b: float(b[name]),
                        filter(show_func, self.benchmarks)))
            ]
        return tuple(data)

    def custom_dataframe(self, *column_fields):
        """return a pandas dataframe with a column for each field in column_fields"""

        # all fields should be present
        def field_present(b):
            if "error_message" in b:
                return False
            for field in column_fields:
                if field not in b:
                    return False
            return True

        data = {}
        for field in column_fields:
            data[field] = list(
                map(lambda b: b[field],
                    filter(field_present, self.benchmarks)))

        df = pd.DataFrame.from_dict(data)
        return df

    def xy_dataframe(self, x_field, y_field):
        """return a pandas dataframe with a column for x_field and y_field"""
        return self.custom_dataframe(*[x_field, y_field])

    def dataframe(self):
        """return a pandas dataframe containing a row for each benchmark object"""
        frames = [pd.DataFrame(b, index=[0]) for b in self.benchmarks]
        return pd.concat(frames, ignore_index=True)

    def stats_dataframe(self, x_field, y_field):
        """return a pandas dataframe containing a row corresponding to each benchmark with x_field, y_field for which aggregate stats can be found"""

        # try to collect aggregate stats for each benchmark name.
        stats = defaultdict(dict)
        for b in self.benchmarks:

            if x_field not in b or y_field not in b or "error_message" in b:
                continue

            name = b["name"]
            if name.endswith("_mean"):
                name = name[:-1 * len("_mean")]
                stats[name]["y_mean"] = b[y_field]
                stats[name]["x_mean"] = b[x_field]
            elif name.endswith("_median"):
                name = name[:-1 * len("_median")]
                stats[name]["y_median"] = b[y_field]
                stats[name]["x_median"] = b[x_field]
            elif name.endswith("_stddev"):
                name = name[:-1 * len("_stddev")]
                stats[name]["y_stddev"] = b[y_field]
                stats[name]["x_stddev"] = b[x_field]
            else:
                continue

        # build columns of data frame.
        # insert NaN for missing data
        columns = {
            "name": [],
            "x_mean": [],
            "y_mean": [],
            "x_median": [],
            "y_median": [],
            "x_stddev": [],
            "y_stddev": [],
        }
        for name in stats:
            columns["name"] += [name]
            columns["x_mean"] += [stats[name].get("x_mean", float('nan'))]
            columns["y_mean"] += [stats[name].get("y_mean", float('nan'))]
            columns["x_median"] += [stats[name].get("x_median", float('nan'))]
            columns["y_median"] += [stats[name].get("y_median", float('nan'))]
            columns["x_stddev"] += [stats[name].get("x_stddev", float('nan'))]
            columns["y_stddev"] += [stats[name].get("y_stddev", float('nan'))]

        df = pd.DataFrame(columns)
        return df

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
