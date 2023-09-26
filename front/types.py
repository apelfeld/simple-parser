
class UnqualifiedType:

    def sizeof(self) -> int:
        raise NotImplementedError

    def alignof(self) -> int:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


class QualifiedType:

    Reference = 1 << 0
    Constant = 1 << 1

    ConstReference = Reference | Constant

    unqualified: UnqualifiedType
    flags: int

    __slots__ = "unqualified", "flags"

    def __init__(self, unqual: UnqualifiedType, flags: int = 0):
        self.unqualified = unqual
        self.flags = flags

    @property
    def is_reference(self) -> bool:
        return bool(self.flags & self.Reference)

    @property
    def is_const(self):
        return bool(self.flags & self.Constant)

    def sizeof(self) -> int:
        return self.unqualified.sizeof()

    def alignof(self) -> int:
        return self.unqualified.alignof()

    def add_flags(self, flags: int):
        return QualifiedType(self.unqualified, self.flags | flags)

    def __repr__(self):
        s = "const " if self.is_const else ""
        s += repr(self.unqualified)
        return s + ("&" if self.is_reference else "")


class VoidType(UnqualifiedType):
    def sizeof(self) -> int:
        return 0

    def alignof(self) -> int:
        return 0

    def __repr__(self):
        return "void"


class IntegerType(UnqualifiedType):
    width: int
    signed: bool

    __slots__ = "width", "signed"

    def __init__(self, w: int, signed: bool = True):
        self.width = w
        self.signed = signed

        assert w & (w - 1) == 0, "Integer width must be a power of two"
        if self.width == 1:
            assert not self.signed, "Integer with width 1 (boolean) must be unsigned"

    def sizeof(self) -> int:
        return self.width

    def alignof(self) -> int:
        return self.width

    def __repr__(self):
        return ("int" if self.signed else "uint") + repr(self.width)


class FloatingType(UnqualifiedType):
    width: int

    __slots__ = "width",

    def __init__(self, width: int):
        self.width = width
        assert width in (32, 64), "width must be 32 or 64 (float or double respectively)"

    def sizeof(self) -> int:
        return self.width

    def alignof(self) -> int:
        return self.width

    def __repr__(self):
        return "float" if self.width == 32 else "double"


class PointerType(UnqualifiedType):

    underlying: QualifiedType

    __slots__ = "underlying",

    def __init__(self, t: QualifiedType):
        self.underlying = t

    def sizeof(self) -> int:
        return 8

    def alignof(self) -> int:
        return 8

    def __repr__(self):
        return f"{self.underlying}*"


class ArrayType(UnqualifiedType):
    underlying: QualifiedType
    count: int

    __slots__ = "underlying", "count"

    def __init__(self, underlying: QualifiedType, count: int):
        self.underlying = underlying
        self.count = count
        assert not self.underlying.is_reference, "There may not be an array of references"

    def sizeof(self) -> int:
        return self.underlying.sizeof() * self.count

    def alignof(self) -> int:
        return self.underlying.alignof()

    def __repr__(self):
        return f"{self.underlying}[{self.count}]"


class TupleType(UnqualifiedType):
    types: list[QualifiedType]
    size: int
    align: int

    __slots__ = "types", "size", "align"

    def __init__(self, types: list[QualifiedType]):
        self.types = []
        size = 0
        align = 0
        for tp in types:
            align = max(align, tp.alignof())
            size += 8 if tp.is_reference else tp.sizeof()
            self.types.append(tp)
        self.size = size
        self.align = align

    def sizeof(self) -> int:
        return self.size

    def alignof(self) -> int:
        return self.align

    def __repr__(self):
        return "(" + ", ".join(repr(x) for x in self.types) + ")"


class FunctionType(UnqualifiedType):
    return_type: QualifiedType
    arguments: list[QualifiedType]

    def __init__(self, ret_type: QualifiedType, arg_types: list[QualifiedType]):
        self.return_type = ret_type
        self.arguments = arg_types

    def sizeof(self) -> int:
        return 0

    def alignof(self) -> int:
        return 0

    def __repr__(self):
        return "fn(" + ", ".join(repr(x) for x in self.arguments) + f") -> {self.return_type}"


__all__ = ["UnqualifiedType", "QualifiedType", "VoidType", "IntegerType", "FloatingType", "PointerType", "ArrayType", "TupleType", "FunctionType"]