import dill

PATH_TO_MODELS = '../models/'
filename = 'catboost_model.dill'

model = PATH_TO_MODELS + filename

PATH_TO_FUNCTIONS = '../extras/'
func_filname = 'functions.dill'

functions = PATH_TO_FUNCTIONS + func_filname

def load_model():
    with open(model, 'rb') as in_strm:
        loaded_model = dill.load(in_strm)
    return loaded_model

def get_process_functions():
    with open(functions, 'rb') as in_strm:
        loaded_func = dill.load(in_strm)
    return loaded_func
