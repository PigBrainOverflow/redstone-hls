import pyrtl
from .core import BasicBlock


def to_pyrtl(bb: BasicBlock, is_top: bool = False) -> pyrtl.Block:
    if not bb.scheduled():
        raise RuntimeError("Scheduling required before lowering.")
    pyrtl.reset_working_block()

    return pyrtl.working_block()