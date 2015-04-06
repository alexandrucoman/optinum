from optinum import algorithm
from optinum import objective

_ALGORITHMS = {
    'HCFirstImprovement': algorithm.HCFirstImprovement,
    'HCBestImprovement': algorithm.HCBestImprovement,
}
_OBJECTIVE_FUNCTION = {
    'Rosenbrock': objective.Rosenbrock,
    'Rastrigin': objective.Rastrigin,
    'Griewangk': objective.Griewangk,
    'SixHumpCamelBack': objective.SixHumpCamelBack,
}


def algorithm(algorithm):
    return _ALGORITHMS.get(algorithm)


def objective_function(function_name):
    return _OBJECTIVE_FUNCTION.get(function_name)()
