import pandas as pd
from pyomo.environ import *
import pyomo.environ as op

# read the data from CSV using pandas
df = pd.read_csv('Dij_matrix.csv', header=0, index_col=0)

# create a dictionary to represent the table
N = 9
d = {(int(m),int(n)): df.iloc[int(m)-1, int(n)-1] for m in df.index for n in df.columns}

a = 3
b = 3

# creating the model
model = ConcreteModel(name="(Facility Layout)")

# # Declaring Decision Varibles
model.X = Var([(i,j,k) for i in range(1, N+1) for j in range(1, a+1) for k in range(1, b+1)], within=Binary)
model.Y = Var([(m,n) for m in range(1,N+1) for n in range(1,N+1)], within=Binary)

def obj_rule(model):
     return sum(sum(d[m, n] * model.Y[m, n] for n in range(m+1,N+1)) for m in range(1,N))

model.obj = Objective(rule = obj_rule,sense=minimize)

print("Objective:")
model.obj.pprint()

model.con1=ConstraintList()

for j in range(1, a+1):
     for k in range(1, b+1):
          model.con1.add(sum((model.X[i,j,k]) for i in range(1,N+1)) == 1)

print("Constraint 1:")
# model.con1.pprint()

model.con2=ConstraintList()
for i in range(1,N+1):
     model.con1.add(sum(sum((model.X[i,j,k]) for k in range(1,b+1)) for j in range(1,a+1))==1)

print("Constraint 2:")
# model.con2.pprint()

model.con3 = ConstraintList()
for j in range(1, a+1):
        for k in range(1, b+1):
            for m in range(1, N+1):
                for n in range (1, N+1): 
                    if 1 <= m and m < n and n <= N+1:
                         try:
                              model.con3.add((model.Y[n,m]) >= ((model.X[m, j, k]) + 1/4 * (model.X[n,j+1,k] + model.X[n,j,k+1] + model.X[n,j-1,k] + model.X[n,j,k-1]) - 1))
                         except:
                              pass
print("Constraint 3:")
# model.con3.pprint()

def con4_rule(model):
   return sum(sum(model.Y[m,n]for n in range(m+1, N+1)) for m in range(1, N+1)) == 2*(N-sqrt(N))
model.con4 = Constraint(rule = con4_rule)

print("Constraint 4:")
# model.con4.pprint()

# solve the model and report the results
solver = SolverFactory('gurobi')
print("Starting solver...")
solver.options['TimeLimit'] = 120
result = solver.solve(model)
print(result)
print("Objective value : " + str(value(model.obj)))

print("Xijk:")
model.X.pprint()
