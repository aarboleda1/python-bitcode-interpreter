import dis  # wait so some things survived the fire?
import marshal
import sys

assert sys.version_info[:2] == (2, 7)


def parse_pyc(f):
    """
    Given a Python 2.7 .pyc file, read the key information and unmarshall and
    return the code object.
    """
    magic_number = f.read(4)
    assert magic_number.encode('hex') == '03f30d0a'
    f.read(4)  # next 4 bytes is the timestamp
    return marshal.load(f)

OP = {
    'NOP': 9,
    'PRINT_ITEM': 71,
    'PRINT_NEWLINE': 72,
    'LOAD_CONST': 100,
    'RETURN_VALUE': 83,
    'BINARY_DIVIDE': 21,
    'STORE_NAME': 90,
    'LOAD_NAME': 101,
    'BINARY_ADD': 23,
    'BINARY_MODULO': 22,
    'MAKE_FUNCTION': 132,
    'CALL_FUNCTION': 131,		
}

HAVE_ARGUMENT = 90  # opcodes from here on have an argument
myDict = {}

def interpret(code):
    """
    Given a code object, interpret (evaluate) the code.
    """
    bytecode = iter(code.co_code)
    values = []

    while True:
        try:
            opcode = ord(bytecode.next())
        except StopIteration:
            break
        if opcode >= HAVE_ARGUMENT:
            # (next_instr[-1]<<8) + next_instr[-2]
            oparg = ord(bytecode.next()) + (ord(bytecode.next()) << 8)

        if opcode == OP['NOP']:
            continue
        elif opcode == OP['LOAD_CONST']:
            values.append(code.co_consts[oparg])
        elif opcode == OP['PRINT_ITEM']:
            print values.pop()
        elif opcode == OP['PRINT_NEWLINE']:
            print
        elif opcode == OP['RETURN_VALUE']:
            return values.pop()
        elif opcode == OP['BINARY_DIVIDE']:
            val1 = values.pop()
            val2 = values.pop()
            values.append(val2 / val1)
        elif opcode == OP['STORE_NAME']:
            myDict[oparg] = values.pop()
        elif opcode == OP['LOAD_NAME']:
            values.append(myDict[oparg])
        elif opcode == OP['BINARY_ADD']:
            val1 = values.pop()
            val2 = values.pop()
            values.append(val1 + val2)
        elif opcode == OP['BINARY_MODULO']:
            val1 = values.pop()
            val2 = values.pop()
            values.append(val2 % val1)
        elif opcode == OP['MAKE_FUNCTION']:
            v = values.pop()
            print v.co_lnotab, ' is the value'
            values.append(v.co_consts)
            """
						Very stuck at the moment
						How to create a function from a code object ?
            https://github.com/python/cpython/blob/2.7/Python/ceval.c
            https://github.com/python/cpython/blob/2.7/Include/opcode.h
						https://late.am/post/2012/03/26/exploring-python-code-objects.html
       
						// taken from the cpython library, 
			  TARGET(MAKE_FUNCTION)
        {
            v = POP(); /* code object */
            x = PyFunction_New(v, f->f_globals);
            Py_DECREF(v);
            /* XXX Maybe this should be a separate opcode? */
            if (x != NULL && oparg > 0) {
                v = PyTuple_New(oparg);
                if (v == NULL) {
                    Py_DECREF(x);
                    x = NULL;
                    break;
                }
                while (--oparg >= 0) {
                    w = POP();
                    PyTuple_SET_ITEM(v, oparg, w);
                }
                err = PyFunction_SetDefaults(x, v);
                Py_DECREF(v);
            }
            PUSH(x);
            break;
        }
						
						"""
        elif opcode == OP['CALL_FUNCTION']:
            print values[0].co_lnotab
        else:
            print 'Unknown opcode {}'.format(opcode)


if __name__ == '__main__':
    """
    Unmarshall the code object from the .pyc file reference as a command
    line argument, and intrepret it.

    Usage: python interpreter.py 1.pyc
    """
    f = open(sys.argv[1], 'rb')
    code = parse_pyc(f)
    dis.dis(code)  # helpful for debugging! but kinda cheating
    print('Interpreting {}...\n'.format(sys.argv[1]))
    ret = interpret(code)
    print('\nFinished interpreting, and returned {}'.format(ret))
