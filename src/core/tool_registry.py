class ToolRegistry:
    functions = {}

    @classmethod
    def register_function(cls, function_cls):
        cls.functions[function_cls.get_name()] = function_cls

    @classmethod
    def get_available_functions(cls):
        return cls.functions
    
    @classmethod
    def get_available_function_names(cls):
        return list(cls.functions.keys())
    

def register_fn(cls):
    ToolRegistry.register_function(cls)
    return cls