/- Dump the Lean-defined CNF as DIMACS, to cross-check against the generator
output (engineering sanity check only; soundness does not depend on it). -/
import P13.Encoding

def main (args : List String) : IO Unit := do
  let out := args.headD "dump.cnf"
  IO.FS.writeFile out (Std.Sat.CNF.dimacs P13.pmdCnf)
