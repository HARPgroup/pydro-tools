# from [name of the module] import [name of the class]
from car import Car

# create objects (you don't have to pass in "self")
car_1 = Car("Chevy","Corvette",2021,"blue")
car_2 = Car("Ford","Mustang",2022,"red")

# access some of this object's attributtes
print(car_1.make)
print(car_1.model)
print(car_1.year)
print(car_1.color)

# use this object's methods 
car_1.drive()
car_2.stop()