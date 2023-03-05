import pandas as pd
from pyomo.environ import *
from pyomo.environ import value

# read the data from CSV using pandas
df = pd.read_csv('Dij_matrix.csv', header=0, index_col=0)

# create a dictionary to represent the table
d = {(int(m),int(n)): df.iloc[int(m)-1, int(n)-1] for m in df.index for n in df.columns}
print(d[(2, 3)])
for key, value in d.items():
    print(key, value)

N = int(input('Enter N value: '))
a=3
b=3

# creating the model
model = ConcreteModel(name="(Facility Layout)")
solver = SolverFactory('gurobi')

# Declaring Decision Varibles
model.x = Var([(i,j,k) for i in range(1, N+1) for j in range(1, a+1) for k in range(1, b+1)], within=Binary)
model.y = Var([(int(m), int(n)) for m in df.index for n in df.columns], within=Binary)
#model.d = Var([(m,n) for m in range(1,9) for n in range(1,9)], within=NonNegativeIntegers)

# objective function
def obj_rule(model):
     #return sum(sum(model.d[m, n] * model.y[m, n] for m in range(1,N+1)) for n in range(m+1,N+1))
     return sum(d[(int(m), int(n))] * model.y[(int(m), int(n))] for m in df.index for n in df.columns)
model.obj = Objective(rule = obj_rule,sense=minimize)

## Defining Constraints
def constraint_layer(model, i):
    return sum(model.x[i, j, k] for j in range(1, a+1) for k in range(1, b+1)) == 1

model.layer_constraint = Constraint(range(1, N+1), rule=constraint_layer)


def constraint_1(model):
     return sum(model.x[i, j, k] for i in range(1,N+1) for j in range(1,a+1) for k in range(1,b+1)) == 1

model.one_constraint = Constraint(rule = constraint_1)

def constraint_3(model):
    #return sum(sum(model.y[m,n] for m in range(1,N+1) for n in range(m+1,N+1)))==2*(N-N^0.5)
    return sum(model.y[(int(m), int(n))] for m in df.index for n in df.columns if int(m) < int(n)) == 2 * (N - N ** 0.5) 
model.three_constraint = Constraint(rule = constraint_3)

model.two_constraint = ConstraintList()
for m in df.index:
    for n in df.index:
        if  1<=int(m) < int(n) <=N:
            for j in range(2, a):
                for k in range(2, b):
                    model.two_constraint.add(model.y[int(m), int(n)] >= model.x[int(m),j,k] + 1/4 * (model.x[int(n),j+1,k] + model.x[int(n),j-1,k] + model.x[int(n),j,k-1]) - 1)




results = solver.solve(model)
if results.solver.status == SolverStatus.ok:
    obj_val = value(model.obj)
    print("Optimal Solution Found")
    print("Objective value : " + str(obj_val))
else:
    print("Solver Status: " + str(results.solver.status))








