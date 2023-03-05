import pandas as pd
from pyomo.environ import *

# read the data from CSV using pandas
df = pd.read_csv('Dij_matrix.csv', header=0, index_col=0)

# create a dictionary to represent the table
d = {(int(m),int(n)): df.iloc[int(m)-1, int(n)-1] for m in df.index for n in df.columns}
print(d[(2, 3)])

N = 9
a=3
b=3

# creating the model
model = ConcreteModel(name="(Facility Layout)")
solver = SolverFactory('gurobi')

# Declaring Decision Varibles
model.x = Var([(i,j,k) for i in range(1, N+1) for j in range(1, a+1) for k in range(1, b+1)], within=Binary)
model.y = Var([(m,n) for m in range(1,9) for n in range(1,9)], within=Binary)
model.d = Var([(m,n) for m in range(1,9) for n in range(1,9)], within=NonNegativeIntegers)

# objective function
def obj_rule(model):
     #return sum(sum(model.d[m, n] * model.y[m, n] for m in range(1,N+1)) for n in range(m+1,N+1))
     return sum(model.d[m, n] * model.y[m, n] for m in range(1,9) for n in range(1,9) if m < n)
model.obj = Objective(rule = obj_rule,sense=minimize)

## Defining Constraints
# layer_constraints = [constraint_layer(model, i) for i in range(1, N+1)]
# model.layer_constraint = ConstraintList(layer_constraints)
# layer_constraints = [constraint_layer(model, i) for i in range(1, N+1)]
# model.layer_constraint = ConstraintList(layer_constraints)



def constraint_1(model):
     return sum(model.x[i, j, k] for i in range(1,N+1) for j in range(1,a+1) for k in range(1,b+1)) == 1

model.one_constraint = Constraint(rule = constraint_1)

def constraint_3(model):
    #return sum(sum(model.y[m,n] for m in range(1,N+1) for n in range(m+1,N+1)))==2*(N-N^0.5)
    return sum(model.y[m,n] for m in range(1,9) for n in range(1,9) if m < n) == 2 * (N - int(N ** 0.5)) 
model.three_constraint = Constraint(rule = constraint_3)
# def constraint_2(model,N,a,b):
#     for m in range(1, N):
#         for n in range(m+1, N+1):
#             for j in range(1, a+1):
#                 for k in range(1, b+1):
#                     return model.y[m,n] >= model.x[m,j,k] + 1/4 * (model.x[n,j+1,k] + model.x[n,j-1,k] + model.x[n,j,k-1]) - 1

#model.two_constraint = Constraint(rule = constraint_2)
model.two_constraint = ConstraintList()
for m in range(1,9):
    for n in range(1,9):
        if  1<=m < n <=N:
            for j in range(2, a):
                for k in range(2, b):
                    model.two_constraint.add(model.y[m,n] >= model.x[int(m),j,k] + 1/4 * (model.x[int(n),j+1,k] + model.x[int(n),j-1,k] + model.x[int(n),j,k-1]) - 1)




# solve the model and report the results
print("Starting solver...")
solver.options['TimeLimit'] = 60
solver.solve(model)
model.pprint()
print("Objective value : " + str(value(model.obj)))




