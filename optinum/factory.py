from optinum.algorithm import hillclimbing
from optinum import objective

_ALGORITHMS = {
    'HCFirstImprovement': hillclimbing.HCFirstImprovement,
    'HCBestImprovement': hillclimbing.HCBestImprovement,
}
_OBJECTIVE_FUNCTION = {
    'Rosenbrock': objective.Rosenbrock,
    'Rastrigin': objective.Rastrigin,
    'Griewangk': objective.Griewangk,
    'SixHumpCamelBack': objective.SixHumpCamelBack,
}


def algorithm(algorithm=None):
    if not algorithm:
        return _ALGORITHMS.keys()
    return _ALGORITHMS.get(algorithm)


def objective_function(function_name=None):
    if not function_name:
        return _OBJECTIVE_FUNCTION.keys()
    return _OBJECTIVE_FUNCTION.get(function_name)()
