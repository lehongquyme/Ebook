import sys
print("version : "+ sys.version)
print(complex(3,2))
# code to test slicing
tuple1 = (0 ,1, 2, 3)

print(tuple1[1:])
print(tuple1[::2])
print(tuple1[2:4])
# tuple with different datatypes
tuple_obj = ("immutable",True,23)
print(tuple_obj)


# Code for converting a list and a string into a tuple
list1 = [0, 1, 2]
 
print(tuple(list1))
 
# string 'python'
print(tuple('python'))


# python code for creating tuples in a loop
tup = ('geek',)
 
# Number of time loop runs
n = 5
for i in range(int(n)):
    tup = (tup,)
    print(tup)

i = 1
while (i < 10):
    i += 1
print(i)
