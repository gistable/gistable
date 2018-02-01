"""
    This code exemplify the use of metaclasses, decorators and signals in python3
"""

# key = function name : value = message to show result
OPERATIONS_MESSAGES = {
    'sum_numbers' : 'A soma é',
    'multiply_numbers' : 'A multiplicação é'
}

class Decorator():
    """ 
        Class to put decorators
    """

    def operation_decorator(operation_function):
        """ 
            Show the result message  
        """
        def decorator(*args):
            function_name = operation_function.__name__ 
            print (OPERATIONS_MESSAGES[function_name])
            return operation_function(*args)

        return decorator

class Signal():
    """ A basic Signal class """

    def __init__(self):
        self.functions = [] 

    def connect(self, function):
        """ 
            Connect a function that will be executed when signal is sent
        """
        self.functions.append(function) 

    def send(self, *args, **kwargs):
        """
            Execute the connected functions
        """
        for function in self.functions:
            function(*args, **kwargs)


class CalculatorMeta(type):

    """ Meta class for calculator that overrides the magic methods __init__ and __new__"""

    def __new__(cls, *args, **kwargs):
        """
            Called when the class is been created
        """
        cls.print_message_new()
        return super(CalculatorMeta, cls).__new__(cls, *args, **kwargs)

    def __init__(cls, class_name, bases, attrs):
        """
            Called when the class was created
        """
        cls.print_message_init()
        super(CalculatorMeta, cls).__init__(class_name, bases, attrs)

    def print_message_init(cls):
        print ("Nova calculadora criada\n")

    def print_message_new():
        print ("Criando nova calculadora...\n\n")


class Calculator(metaclass=CalculatorMeta):
    def __init__(self, numbers):
        self.numbers = numbers
        
        # Create a signal 
        self.sum_signal = self.create_sum_signal() 
        
        self.sum_numbers()  

    def create_sum_signal(self):
        sum_signal = Signal()
        # Connect the function sum_next to the signal
        sum_signal.connect(self.sum_next)

        return sum_signal

    @Decorator.operation_decorator
    def sum_numbers(self):
        result = 0
        for value in self.numbers:
            result += value

        print ("\t\t\t" + str(result))
        self.sum_signal.send()

    # This function is called by the signal
    def sum_next(self):
        self.multiply_numbers()

    @Decorator.operation_decorator
    def multiply_numbers(self):
        result = 1
        for value in self.numbers:
            result *= value

        print ("\t\t\t" + str(result))


calc = Calculator([1,2,3])