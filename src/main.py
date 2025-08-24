from typing import List

from z3 import *

# オペレーションを表現する
class Operation:
  def __init__(self, makespan: int, num: int, duration: int):
    self.makespan = makespan
    self.num = num
    self.name = "op[{}]".format(self.num)
    self.duration = duration
    self.start_at_or_later: List[Bool] = [] # オペレーションはこの時間以降開始される（この時間も含む）
    for t in range(0, self.makespan + 1): # inclusiveにしたいので +1
      self.start_at_or_later.append(Bool("{}.sa[{}]".format(self.name, t)))
    self.start_at = -1  # あとでモデルから埋める

  def decode(self, model: 'ModelRef'):
    for t in range(0, self.makespan + 1):
      if model.eval(self.start_at_or_later[t]):
        self.start_at = max(self.start_at, t)
    print("{}: {} -> {}".format(self.name, self.start_at, self.start_at + self.duration))

  def validate(self, model: 'ModelRef') -> bool:
    for t in range(0, self.makespan + 1):
      start_at_or_later_t = model.eval(self.start_at_or_later[t])
      if start_at_or_later_t and t > self.start_at:
        return False
      if not start_at_or_later_t and t <= self.start_at:
        return False
    return self.start_at + self.duration <= self.makespan

# 資源制約（aとbは同時に実行できない）を表現する
class ResourceConstraint:
  def __init__(self, a: 'Operation', b: 'Operation'):
    self.a = a
    self.b = b
    self.precede_a = Bool("pr({},{})".format(a.num, b.num))
    self.precede_b = Bool("pr({},{})".format(b.num, a.num))

  def validate(self, model: 'ModelRef') -> bool:
    if model.eval(self.precede_a):
      return self.a.start_at + self.a.duration <= self.b.start_at
    if model.eval(self.precede_b):
      return self.b.start_at + self.b.duration <= self.a.start_at
    return False

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
    # 1. 資源制約があるなら、どちらかが先に実行されている
    for rc in self.resource_constraints:
      solver.add(Or(rc.precede_a, rc.precede_b))

    for op in self.operations:
      # 2. 時刻0かそれ以降に始まって、self.makespan - op.duration + 1かそれ以降に始まる事はない
      solver.add(And(op.start_at_or_later[0], Not(op.start_at_or_later[self.makespan - op.duration + 1])))
      # 3. 時刻tかそれ以降に開始しているなら、時刻t-1かそれ以降でも開始している（start_at_or_laterの定義）
      for t in range(1, self.makespan + 1):
        # op.start_at_or_later[t] -> op.start_at_or_later[t - 1] を同値変形した形
        solver.add(Or(Not(op.start_at_or_later[t]), op.start_at_or_later[t - 1]))

      # 4. 資源制約を記述する
      for rc in self.resource_constraints:
        # rc.aが先行しているなら、rc.bはrc.aの実行後に開始される
        for t in range(0, self.makespan - rc.a.duration + 1):
          # (rc.precede_a and rc.a.start_at[t]) -> rc.b.start_at_or_later[t + op.duration] を同値変形した形
          solver.add(Or(Not(rc.precede_a), Not(rc.a.start_at_or_later[t]), rc.b.start_at_or_later[t + rc.a.duration]))
        # rc.bが先行しているなら、rc.aはrc.bの実行後に開始される
        for t in range(0, self.makespan - rc.b.duration + 1):
          # (rc.b.start_at[t] and rc.precede_b) -> rc.a.start_at_or_later[t + op.duration] を同値変形した形
          solver.add(Or(Not(And(rc.precede_b, rc.b.start_at_or_later[t])), rc.a.start_at_or_later[t + rc.b.duration]))

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
  solver = Solver()
  problem = Problem(makespan = 1168)
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
  else:
    print("Unsatisfiable")

if __name__ == "__main__":
  main()
