import os
from collections import namedtuple

import torch
import torch.nn as nn

def get_model_summary(model, input_shape, item_length=26, verbose=True):
    if len(input_shape) == 2:
        input_shape = (1, 3, ) + tuple(input_shape)
    elif len(input_shape) == 3:
        input_shape = (1, ) + tuple(input_shape)

    if isinstance((input_shape), torch.Tensor):
        input_tensors = input_shape
    else:
        input_tensors = torch.rand(input_shape)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    input_tensors = input_tensors.to(device)

    summary = []

    ModuleDetails = namedtuple(
        "Layer", ["name", "input_size", "output_size", "num_parameters", "multiply_adds"])
    hooks = []
    layer_instances = {}

    def add_hooks(module):

        def hook(module, input, output):
            class_name = str(module.__class__.__name__)

            instance_index = 1
            if class_name not in layer_instances:
                layer_instances[class_name] = instance_index
            else:
                instance_index = layer_instances[class_name] + 1
                layer_instances[class_name] = instance_index

            layer_name = class_name + "_" + str(instance_index)

            params = 0

            if class_name.find("Conv") != -1 or class_name.find("BatchNorm") != -1 or \
               class_name.find("Linear") != -1:
                for param_ in module.parameters():
                    params += param_.view(-1).size(0)
            flops = 0
            if isinstance(output, list):
                for op in output:
                    flops += params * torch.prod(torch.LongTensor(list(op.size())[2:])).item()
            else:
                flops = params * torch.prod(torch.LongTensor(list(output.size())[2:])).item()
            
            if isinstance(input[0], list):
                input = input[0]
            if isinstance(output, list):
                output = output[0]

            summary.append(
                ModuleDetails(
                    name=layer_name,
                    input_size=list(input[0].size()),
                    output_size=list(output.size()),
                    num_parameters=params,
                    multiply_adds=flops)
            )

        if not isinstance(module, nn.ModuleList) \
           and not isinstance(module, nn.Sequential) \
           and module != model:
            hooks.append(module.register_forward_hook(hook))

    model.eval()
    model.apply(add_hooks)

    space_len = item_length

    model(input_tensors)
    for hook in hooks:
        hook.remove()

    details = ''
    if verbose:
        details = "Model Summary" + \
            os.linesep + \
            "Name{}Input Size{}Output Size{}Parameters{}Multiply Adds (Flops){}".format(
                ' ' * (space_len - len("Name")-12),
                ' ' * (space_len - len("Input Size")-8),
                ' ' * (space_len - len("Output Size")-8),
                ' ' * (space_len - len("Parameters")-8),
                ' ' * (space_len - len("Multiply Adds (Flops)"))) \
                + os.linesep + '-' * space_len * 4 + os.linesep

    params_sum = 0
    flops_sum = 0
    name_max_len = 0
    for layer in summary:
        params_sum += layer.num_parameters
        if layer.multiply_adds != "N/A":
            flops_sum += layer.multiply_adds
            if layer.num_parameters > 0 and layer.multiply_adds > 0 and len(layer[0]) > name_max_len:
                name_max_len = len(layer[0])

    for layer in summary: 
        if verbose and layer.num_parameters > 0 and layer.multiply_adds > 0:
            details += "{}{}{}{}{}{}{}{}{:.3f}{}{}{}{:.3f}{}".format(
                layer.name,
                ' ' * (name_max_len - len(layer.name)+4),
                layer.input_size,
                ' ' * (space_len - len(str(layer.input_size))-8),
                layer.output_size,
                ' ' * (space_len - len(str(layer.output_size))-8),
                layer.num_parameters,
                ' ' * (space_len - len(str(layer.num_parameters))-16),
                float(layer.num_parameters) * 100.0 / params_sum,
                ' ' * (space_len - len(str(layer.num_parameters))-16),
                layer.multiply_adds,
                ' ' * (space_len - len(str(layer.multiply_adds))-16),
                float(layer.multiply_adds) * 100.0 / flops_sum, os.linesep)
    details += '-' * space_len * 4 + os.linesep

    details += "Total Parameters: "
    if params_sum > 1024**3:
        details += '{:.3f}G'.format(params_sum/(1024**3))
    elif params_sum > 1024**2:
        details += '{:.3f}M'.format(params_sum/(1024**2))
    else:
        details += '{:.3f}K'.format(params_sum/(1024))
    details +=  ' ({:,})'.format(params_sum)

    details += "    Total Multiply Adds: "
    if flops_sum > 1024**3:
        details += '{:.3f}G'.format(flops_sum/(1024**3))
    elif flops_sum > 1024**2:
        details += '{:.3f}M'.format(flops_sum/(1024**2))
    else:
        details += '{:.3f}K'.format(flops_sum/(1024))
    details += 'FLOPs ({})'.format(flops_sum) + os.linesep
    
    details += "Number of Layers" + os.linesep
    for layer in layer_instances:
        details += "{} : {} layers   ".format(layer, layer_instances[layer])

    return details