from z3 import *

def main():
  a = Bool("a")
  b = Bool("b")
  c = Bool("c")
  solver = Solver()
  solver.add(And(Or(a, c), Or(Not(a), b, Not(c))))
  if solver.check() == sat:
    model = solver.model()
    print("Satisfiable")
    print("a = {}".format(model.eval(a)))
    print("b = {}".format(model.eval(b)))
    print("c = {}".format(model.eval(c)))
  else:
    print("Unsatisfiable")

if __name__ == "__main__":
  main()
