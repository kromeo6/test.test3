from typing import NamedTuple
from kfp.v2.dsl import component, Output, Metrics
from kfp import dsl, compiler


@component
def add(a: float, b: float) -> float:
    return a + b

@component(packages_to_install=['numpy'])
def my_divmod(dividend: float, divisor: float, metrics: Output[Metrics]) -> NamedTuple('MyDivmodOutput', [('quotient', float), ('remainder', float)]):
    
    '''Divides two numbers and calculate the quotient and remainder'''

    import numpy as np

    # Define a helper function
    def divmod_helper(dividend, divisor):
        return np.divmod(dividend, divisor)

    (quotient, remainder) = divmod_helper(dividend, divisor)

    # Export two metrics
    metrics.log_metric('quotient', float(quotient))
    metrics.log_metric('remainder', float(remainder))

    from collections import namedtuple
    divmod_output = namedtuple('MyDivmodOutput',
        ['quotient', 'remainder'])
    
    return divmod_output(float(quotient), float(remainder))

@dsl.pipeline(
   name='calculation-pipeline',
   description='An example pipeline that performs arithmetic calculations.'
)
def calc_pipeline(a: float=1, b: float=7, c: float=17):
    add_task = add(a=a, b=4.)
    divmod_task = my_divmod(dividend=add_task.output, divisor=b)
    result_task = add(a=divmod_task.outputs['quotient'], b=c)

compiler.Compiler().compile(calc_pipeline, 'calc-pipeline.yaml')

# kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(
#     calc_pipeline,
#     arguments=arguments,
#     mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE)
