import pandas as pd
from pyomo.environ import *
import pyomo.environ as op

# read the data from CSV using pandas
df = pd.read_csv('Dij_matrix.csv', header=0, index_col=0)

# create a dictionary to represent the table
N = 9
# while N <= 0 or N > 9:
#     N = int(input('Enter N value >0 and <= 9: '))

d = {(int(m),int(n)): df.iloc[int(m)-1, int(n)-1] for m in df.index for n in df.columns}

a = 3
b = 3

# creating the model
model = ConcreteModel(name="(Facility Layout)")

# # Declaring Decision Varibles
model.X = op.Var([(i,j,k) for i in range(1, N+1) for j in range(1, a+1) for k in range(1, b+1)], within=Binary)
model.Y = op.Var([(m,n) for m in range(1,N+1) for n in range(1,N+1)], within=Binary)
model.C = op.Var([(m,n) for m in range(1,N+1) for n in range(1,N+1)], within=NonNegativeIntegers)

# objective function
# def obj_rule(model):
#     return sum(sum((1/model.C[m,n])*model.Y[m,n] for n in range(1, m + 1)) for m in range(1, N))


# def obj_rule(model):
#      t_sum = 0.0
#      for m in range (1,N):
#         for n in range (m +1, N):
#             #t_sum += sum(inv(model.C[m,n])*model.Y[m,n])
#             t_sum += (1 / model.C[m,n]) * model.Y[m,n]
#      return t_sum

def obj_rule(model):
     #return sum(sum(model.d[m, n] * model.y[m, n] for m in range(1,N+1)) for n in range(m+1,N+1))
     return sum(d[(int(m), int(n))] * model.Y[(int(m), int(n))] for m in df.index for n in df.columns)

model.obj = Objective(rule = obj_rule,sense=minimize)

## Defining Constraints
def con1_rule(model):
    return (sum((model.X[i,j,k]) for i in range(1, N) for j in range(1, a) for k in range(1, b))) == 1

def con2_rule(model):
    return (sum(sum((model.X[i,j,k]) for i in range(1, N) for k in range(1, b)) for j in range(1, a))) == 1
    
def con4_rule(model):
    return sum(sum(model.Y[m,n]for n in range(m+1, N)) for m in range(1, N)) == 2*(N-sqrt(N))

model.con1 = Constraint(rule = con1_rule)
model.con2 = Constraint(rule = con2_rule)
model.con3 = ConstraintList()
for j in range(2, a):
        for k in range(2, b):
            for m in df.index:
                for n in df.index: 
                    if 1 <= m < n <= N:
                        model.con3.add((model.Y[n,m]) >= (model.X[m, j, k]) + 1/4 * (model.X[n,j+1,k] + model.X[n,j-1,k] + model.X[n,j,k-1]))

model.con4 = Constraint(rule = con4_rule)


# solve the model and report the results
solver = SolverFactory('gurobi')
print("Starting solver...")
solver.options['TimeLimit'] = 120
result = solver.solve(model)
print(result)
print("Objective value : " + str(value(model.obj)))
