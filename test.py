import numpy as np
class Neuron:
    def __init__(self, bias, weight):
        self.bias = bias
        self.weight = weight
        self.inputs = None
    def forward_pass(self, inputs):
        self.inputs = inputs
        z = np.dot(inputs, self.weight) + self.bias
        return self.activation(z)

    def activation(self, x):
        return 1 / (1 + np.exp(-x))


def test_neuron():
    # Create a neuron with bias and weight
    bias = 0.5
    weight = np.array([0.2, 0.8])
    neuron = Neuron(bias, weight)

    # Test input
    inputs = np.array([1.0, 0.5])
    
    # Forward pass
    output = neuron.forward_pass(inputs)
    print(f"Inputs: {inputs}")
    print(f"Output: {output}")

test_neuron()