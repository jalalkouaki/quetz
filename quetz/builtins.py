"""
Quetz Standard Library Built-in Functions
"""

from __future__ import annotations
import os
import time
from typing import TYPE_CHECKING

from quetz.callables import QuetzNativeFunction, QuetzCallable
from quetz.errors import QuetzRuntimeError

if TYPE_CHECKING:
    from quetz.interpreter import Interpreter


def init_builtins(interpreter: Interpreter):
    from quetz.interpreter import is_truthy, stringify

    def _print(interp: Interpreter, args, line, col):
        text = " ".join(stringify(a) for a in args)
        if interp.output_buffer is not None:
            interp.output_buffer.append(text)
        else:
            print(text)
        return None

    def _len(interp: Interpreter, args, line, col):
        arg = args[0]
        if isinstance(arg, (str, list, dict)):
            return float(len(arg))
        raise QuetzRuntimeError("len() expects string, list, or map.", line, col, interp.current_source)

    def _push(interp: Interpreter, args, line, col):
        lst, val = args[0], args[1]
        if not isinstance(lst, list):
            raise QuetzRuntimeError("push() expects list as first argument.", line, col, interp.current_source)
        lst.append(val)
        return lst

    def _pop(interp: Interpreter, args, line, col):
        lst = args[0]
        if not isinstance(lst, list):
            raise QuetzRuntimeError("pop() expects list as first argument.", line, col, interp.current_source)
        if len(lst) == 0:
            raise QuetzRuntimeError("Cannot pop from empty list.", line, col, interp.current_source)
        return lst.pop()

    def _keys(interp: Interpreter, args, line, col):
        m = args[0]
        if not isinstance(m, dict):
            raise QuetzRuntimeError("keys() expects map as argument.", line, col, interp.current_source)
        return list(m.keys())

    def _values(interp: Interpreter, args, line, col):
        m = args[0]
        if not isinstance(m, dict):
            raise QuetzRuntimeError("values() expects map as argument.", line, col, interp.current_source)
        return list(m.values())

    def _type(interp: Interpreter, args, line, col):
        val = args[0]
        if val is None: return "nil"
        if isinstance(val, bool): return "bool"
        if isinstance(val, (int, float)): return "number"
        if isinstance(val, str): return "string"
        if isinstance(val, list): return "list"
        if isinstance(val, dict): return "map"
        if isinstance(val, QuetzCallable): return "function"
        return "unknown"

    def _str(interp: Interpreter, args, line, col):
        return stringify(args[0])

    def _num(interp: Interpreter, args, line, col):
        val = args[0]
        try:
            return float(val)
        except Exception:
            raise QuetzRuntimeError(f"Cannot convert {val!r} to number.", line, col, interp.current_source)

    def _range(interp: Interpreter, args, line, col):
        if len(args) == 1:
            start, end, step = 0.0, float(args[0]), 1.0
        elif len(args) == 2:
            start, end, step = float(args[0]), float(args[1]), 1.0
        elif len(args) == 3:
            start, end, step = float(args[0]), float(args[1]), float(args[2])
        else:
            raise QuetzRuntimeError("range() expects 1 to 3 arguments.", line, col, interp.current_source)

        if step == 0:
            raise QuetzRuntimeError("range() step cannot be zero.", line, col, interp.current_source)

        res = []
        cur = start
        if step > 0:
            while cur < end:
                res.append(cur)
                cur += step
        else:
            while cur > end:
                res.append(cur)
                cur += step
        return res

    def _clock(interp: Interpreter, args, line, col):
        return time.time()

    def _read_file(interp: Interpreter, args, line, col):
        path = str(args[0])
        full_path = os.path.join(interp.base_dir, path) if not os.path.isabs(path) else path
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise QuetzRuntimeError(f"Failed to read file '{path}': {e}", line, col, interp.current_source)

    def _write_file(interp: Interpreter, args, line, col):
        path = str(args[0])
        content = str(args[1])
        full_path = os.path.join(interp.base_dir, path) if not os.path.isabs(path) else path
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            raise QuetzRuntimeError(f"Failed to write file '{path}': {e}", line, col, interp.current_source)

    def _map(interp: Interpreter, args, line, col):
        lst, fn = args[0], args[1]
        if not isinstance(lst, list):
            raise QuetzRuntimeError("map() expects list as first argument.", line, col, interp.current_source)
        if not isinstance(fn, QuetzCallable):
            raise QuetzRuntimeError("map() expects function as second argument.", line, col, interp.current_source)
        return [fn.call(interp, [item], line, col) for item in lst]

    def _filter(interp: Interpreter, args, line, col):
        lst, fn = args[0], args[1]
        if not isinstance(lst, list):
            raise QuetzRuntimeError("filter() expects list as first argument.", line, col, interp.current_source)
        if not isinstance(fn, QuetzCallable):
            raise QuetzRuntimeError("filter() expects function as second argument.", line, col, interp.current_source)
        return [item for item in lst if is_truthy(fn.call(interp, [item], line, col))]

    def _reduce(interp: Interpreter, args, line, col):
        lst, fn, init = args[0], args[1], args[2]
        if not isinstance(lst, list):
            raise QuetzRuntimeError("reduce() expects list as first argument.", line, col, interp.current_source)
        if not isinstance(fn, QuetzCallable):
            raise QuetzRuntimeError("reduce() expects function as second argument.", line, col, interp.current_source)
        acc = init
        for item in lst:
            acc = fn.call(interp, [acc, item], line, col)
        return acc

    interpreter.globals.define("print", QuetzNativeFunction("print", -1, _print))
    interpreter.globals.define("len", QuetzNativeFunction("len", 1, _len))
    interpreter.globals.define("push", QuetzNativeFunction("push", 2, _push))
    interpreter.globals.define("pop", QuetzNativeFunction("pop", 1, _pop))
    interpreter.globals.define("keys", QuetzNativeFunction("keys", 1, _keys))
    interpreter.globals.define("values", QuetzNativeFunction("values", 1, _values))
    interpreter.globals.define("type", QuetzNativeFunction("type", 1, _type))
    interpreter.globals.define("str", QuetzNativeFunction("str", 1, _str))
    interpreter.globals.define("num", QuetzNativeFunction("num", 1, _num))
    interpreter.globals.define("range", QuetzNativeFunction("range", -1, _range))
    interpreter.globals.define("clock", QuetzNativeFunction("clock", 0, _clock))
    interpreter.globals.define("read_file", QuetzNativeFunction("read_file", 1, _read_file))
    interpreter.globals.define("write_file", QuetzNativeFunction("write_file", 2, _write_file))
    interpreter.globals.define("map", QuetzNativeFunction("map", 2, _map))
    interpreter.globals.define("filter", QuetzNativeFunction("filter", 2, _filter))
    interpreter.globals.define("reduce", QuetzNativeFunction("reduce", 3, _reduce))
