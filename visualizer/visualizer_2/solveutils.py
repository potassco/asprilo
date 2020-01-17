import clingo
import parseutils as pu

def solve_from_file(file, atomcfg):

    ctl = clingo.Control("0")
    ctl.add("p", [], file.read())
    ctl.ground([("p", [])])
    with ctl.solve(yield_=True) as handle:
        model = pu.parse_clingo_model(handle, atomcfg)
    return model