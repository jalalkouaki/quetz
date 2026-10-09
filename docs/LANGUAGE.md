# Quetz Language Specification & Reference (v0.2.0)

Quetz (`.qz`) is an expressive, dynamic, multi-paradigm interpreted programming language.

---

## 1. Syntax & Lexical Grammar

### Comments
```quetz
# This is a line comment
let x = 42 # inline comment
```

### Identifiers & Literals
- **Numbers**: Standard 64-bit floating point numbers (`42`, `3.1415`).
- **Strings**: Single or double quotes (`"hello\n"`, `'world'`).
- **String Interpolation**: Embedded expressions inside string literals using `${expr}`:
  ```quetz
  let name = "Quetz";
  print("Hello, ${name}! 2 + 2 = ${2 + 2}");
  ```
- **Booleans**: `true`, `false`.
- **Nil**: `nil`.

---

## 2. Variables & Operators

### Variable Declaration & Assignment
Variables are declared with `let` and possess lexical block scoping.
```quetz
let message = "Hello, Quetz!";
let count = 0;
```

### Compound Assignment Operators
Quetz supports standard compound assignment operators:
- `+=` Addition / String concatenation / List concatenation
- `-=` Subtraction
- `*=` Multiplication / String repetition / List repetition
- `/=` Division
- `%=` Modulo

```quetz
let x = 10;
x += 5; # 15
x *= 2; # 30
x /= 3; # 10
x %= 4; # 2
```

### Arithmetic & Exponentiation
- Standard arithmetic: `+`, `-`, `*`, `/`, `%`
- Exponentiation: `**` (right-associative)
  ```quetz
  let sq = 3 ** 2;      # 9
  let tower = 2 ** 3 ** 2; # 2 ** 9 = 512
  ```

---

## 3. Control Flow

### If / Else If Chaining
```quetz
if score >= 90 {
    print("Grade: A");
} else if score >= 80 {
    print("Grade: B");
} else if score >= 70 {
    print("Grade: C");
} else {
    print("Grade: F");
}
```

### While Loops
```quetz
let i = 0;
while i < 5 {
    if i == 3 {
        break;
    }
    print(i);
    i += 1;
}
```

### For-In Loops
Iterate over lists, maps (keys), or strings:
```quetz
for item in [10, 20, 30] {
    print(item);
}
```

---

## 4. Functions & Functional Programming

### Named Functions & Default Parameter Values
Functions can specify default parameter values:
```quetz
fn greet(name = "World", greeting = "Hello") {
    return "${greeting}, ${name}!";
}

print(greet());                # Hello, World!
print(greet("Ada"));           # Hello, Ada!
print(greet("Grace", "Welcome")); # Welcome, Grace!
```

### Closures & First-Class Functions
```quetz
fn make_multiplier(factor) {
    return fn(x) {
        return x * factor;
    };
}

let double = make_multiplier(2);
print(double(10)); # 20
```

---

## 5. Error Handling

Structured exception handling with `try`, `catch`, and `throw`:
```quetz
try {
    throw "Fatal database error";
} catch (err) {
    print("Caught error: ${err}");
}
```

---

## 6. Built-in Standard Library

| Function | Signature | Description |
|---|---|---|
| `print(...)` | `print(...args)` | Prints values separated by space; returns `nil` |
| `len(v)` | `len(list \| map \| str)` | Returns collection or string length |
| `push(l, v)`| `push(list, value)` | Appends value to list in-place |
| `pop(l)` | `pop(list)` | Pops and returns last element |
| `keys(m)` | `keys(map)` | Returns list of map keys |
| `values(m)`| `values(map)` | Returns list of map values |
| `type(v)` | `type(value)` | Returns type as string |
| `str(v)` | `str(value)` | Converts value to string representation |
| `num(v)` | `num(value)` | Converts value to numeric float |
| `range(...)`| `range(start, end, step)` | Generates a list of numbers |
| `clock()` | `clock()` | Current Unix timestamp (float) |
| `read_file(p)` | `read_file(path)` | Reads UTF-8 file contents |
| `write_file(p, c)` | `write_file(path, content)` | Writes string content to file |
| `map(l, fn)` | `map(list, fn)` | Transforms list elements via callback |
| `filter(l, fn)` | `filter(list, fn)` | Filters list elements matching predicate |
| `reduce(l, fn, init)` | `reduce(list, fn, init)` | Reduces list elements from left to right |
