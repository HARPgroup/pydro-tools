# this file represents a "module" containing a class or classes
# 
# create a class (class [name of object])
# common convention is for class names to be capital
class Car:
    
    # need a special method that will construct objects for you
    # in other languages this is called the "constructor"
    # self refers to the object that you're currently working on or creating
    # pass in arguments and assign them to each object's attributes
    def __init__(self,make,model,year,color):
        # define the attributes the object may have
        self.make = make
        self.model = model
        self.year = year
        self.color = color

    # define the methods the object may perform
    # self refers to the object that is using this method
    def drive(self):
        print("This "+self.model+" is driving")

    def stop(self):
        print("This "+self.model+" is stopped")
