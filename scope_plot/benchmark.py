#
# Copyright (C) 2017 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import re
import copy

class GoogleBenchmark(object):
    def __init__(self, path):
        self.path = path
    
    def __enter__(self):
        with open(self.path, "rb") as f:
            j = json.loads(f.read().decode("utf-8"))
        self.context = j["context"]
        self.benchmarks = j["benchmarks"]
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def filter_name(self, regex):
        filtered = copy.deepcopy(self)
        pattern = re.compile(regex)
        filtered.benchmarks = [b for b in filtered.benchmarks if pattern.search(b["name"])]
        return filtered

    def filter_field(self, field_name):
        filtered = copy.deepcopy(self)
        filtered.benchmarks = [b for b in filtered.benchmarks if field_name in b]
        return filtered

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

