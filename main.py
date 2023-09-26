from front.parser import *
from front.expression import *
from front.statement import *
from front.types import *

p = Parser("fn func(a: i32, b: i32) -> i32 { var c: i32 = a + b; return c * c + a * b; }")
print(p.parse_module(), "\n") # Print syntax tree
print(p.errors) # Print errors
