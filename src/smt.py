from typing import List

from z3 import *

# オペレーションを表現する
class Operation:
  def __init__(self, makespan: int, num: int, duration: int):
    self.makespan = makespan
    self.num = num
    self.name = "op[{}]".format(self.num)
    self.duration = duration
    self.start_at = Int("{}.start_at".format(self.name))

  def decode(self, model: 'ModelRef'):
    start_at = model.eval(self.start_at)
    end_by = model.eval(self.start_at + self.duration)
    print("{}: {} -> {}".format(self.name, start_at, end_by))

  def validate(self, model: 'ModelRef') -> bool:
    return model.eval(self.start_at + self.duration <= self.makespan)

# 資源制約（aとbは同時に実行できない）を表現する
class ResourceConstraint:
  def __init__(self, a: 'Operation', b: 'Operation'):
    self.a = a
    self.b = b

  def validate(self, model: 'ModelRef') -> bool:
    return model.eval(Xor(
      self.a.start_at + self.a.duration <= self.b.start_at,
      self.b.start_at + self.b.duration <= self.a.start_at,
    ))

# gp03-01を表現する
class Problem:
  # makespanは総時間。この時間内に終わるかどうかをチェック
  def __init__(self, makespan: int):
    self.makespan = makespan
    self.operations: List[Operation] = [
      Operation(self.makespan, 0, 661),
      Operation(self.makespan, 1, 6),
      Operation(self.makespan, 2, 333),
      Operation(self.makespan, 3, 168),
      Operation(self.makespan, 4, 489),
      Operation(self.makespan, 5, 343),
      Operation(self.makespan, 6, 171),
      Operation(self.makespan, 7, 505),
      Operation(self.makespan, 8, 324),
    ]
    self.resource_constraints: List[ResourceConstraint] = []
    self.construct_resource_constraints()

  def construct_resource_constraints(self):
    # 同一のジョブに属するオペレーションは同時に実行できない
    self.resource_constraints.append(ResourceConstraint(self.operations[0], self.operations[1]))
    self.resource_constraints.append(ResourceConstraint(self.operations[0], self.operations[2]))
    self.resource_constraints.append(ResourceConstraint(self.operations[1], self.operations[2]))

    self.resource_constraints.append(ResourceConstraint(self.operations[3], self.operations[4]))
    self.resource_constraints.append(ResourceConstraint(self.operations[3], self.operations[5]))
    self.resource_constraints.append(ResourceConstraint(self.operations[4], self.operations[5]))

    self.resource_constraints.append(ResourceConstraint(self.operations[6], self.operations[7]))
    self.resource_constraints.append(ResourceConstraint(self.operations[6], self.operations[8]))
    self.resource_constraints.append(ResourceConstraint(self.operations[7], self.operations[8]))

    # 同一のマシンを使用するオペレーションは同時に実行できない
    self.resource_constraints.append(ResourceConstraint(self.operations[0], self.operations[3]))
    self.resource_constraints.append(ResourceConstraint(self.operations[0], self.operations[6]))
    self.resource_constraints.append(ResourceConstraint(self.operations[3], self.operations[6]))

    self.resource_constraints.append(ResourceConstraint(self.operations[1], self.operations[4]))
    self.resource_constraints.append(ResourceConstraint(self.operations[1], self.operations[7]))
    self.resource_constraints.append(ResourceConstraint(self.operations[4], self.operations[7]))

    self.resource_constraints.append(ResourceConstraint(self.operations[2], self.operations[5]))
    self.resource_constraints.append(ResourceConstraint(self.operations[2], self.operations[8]))
    self.resource_constraints.append(ResourceConstraint(self.operations[5], self.operations[8]))

  def encode(self, solver: 'Solver'):
    for rc in self.resource_constraints:
      solver.add(Or(
        rc.a.start_at + rc.a.duration <= rc.b.start_at,
        rc.b.start_at + rc.b.duration <= rc.a.start_at,
      ))
    for op in self.operations:
      solver.add(And(0 <= op.start_at, op.start_at + op.duration <= op.makespan))

  def decode(self, model: 'ModelRef'):
    for op in self.operations:
      op.decode(model)

  def validate(self, model: 'ModelRef'):
    ok = True
    for op in self.operations:
      ok = ok and op.validate(model)
    for rc in self.resource_constraints:
      ok = ok and rc.validate(model)
    if ok:
      print("Valid answer")
    else:
      print("Invalid answer")

def main():
  import time
  makespan = 1168
  solver = Solver()
  problem = Problem(makespan)

  beg = time.perf_counter()
  # 問題を論理式に変換する
  problem.encode(solver)
  end = time.perf_counter()
  print("Encoded in {:.2f} sec.".format(end - beg))

  beg = time.perf_counter()
  check = solver.check()
  end = time.perf_counter()
  print("Solved in {:.2f} sec.".format(end - beg))
  if check == sat:
    model = solver.model()
    print("Satisfiable")
    problem.decode(model)
    problem.validate(model)
    print(solver.statistics())
  else:
    print("Unsatisfiable")

if __name__ == "__main__":
  main()
