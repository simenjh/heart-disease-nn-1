import numpy as np
from scipy.special import expit


def init_params(X, activation_layers):
    params = {}
    l = 1
    for n_activation in activation_layers:
        W = None
        b = np.zeros((n_activation, 1))
        if l == 1:
            W = np.random.randn(n_activation, X.shape[0]) * 0.01
        else:
            W = np.random.randn(n_activation, activation_layers[l-2]) * 0.01
  
        params[f"W{l}"] = W
        params[f"b{l}"] = b
        l += 1
        
    return params



def train_model(X, y, parameters, iterations, learning_rate, reg_param):
    logging_frequency = 10
    costs_iterations = {"costs": [], "iterations": []}
    
    for i in range(iterations):
        AL, caches = forward_propagation(X, parameters)
        cost = compute_cost(AL, y, parameters, reg_param)

        if i % logging_frequency == 0:
            costs_iterations["costs"].append(cost)
            costs_iterations["iterations"].append(i)
        
        gradients = backprop(AL, y, caches)
        update_parameters(parameters, gradients, learning_rate, reg_param)
    return costs_iterations, parameters
        



def train_various_sizes(X_train, X_cv, y_train, y_cv, parameters, activation_layers, iterations, learning_rate, reg_param):
    costs_train, costs_cv, m_examples = [], [], []
    for i in range(1, X_train.shape[1], 20):
        parameters = init_params(X_train, activation_layers)
        costs_iterations, parameters = train_model(X_train[:, :i], y_train[:, :i], parameters, iterations, learning_rate, reg_param)

        AL_cv, caches = forward_propagation(X_cv, parameters)
        cost_cv = compute_cost(AL_cv, y_cv, parameters, reg_param)

        costs_train.append(costs_iterations["costs"][-1])
        costs_cv.append(cost_cv)
        m_examples.append(i)

    return costs_train, costs_cv, m_examples









        
        

    
    
def backprop(AL, y, caches):
    grads = {}
    L = len(caches)
    m = AL.shape[1]
    y = y.reshape(AL.shape)
    epsilon = 1e-10

    dAL = - (np.divide(y, AL + epsilon) - np.divide(1 - y, 1 - AL + epsilon))

    current_cache = caches[L-1]
    grads[f"dA{L-1}"], grads[f"dW{L}"], grads[f"db{L}"] = linear_activation_backward(dAL, current_cache, "sigmoid")

    for l in reversed(range(L-1)):
        current_cache = caches[l]
        grads[f"dA{l}"], grads[f"dW{l+1}"], grads[f"db{l+1}"] = linear_activation_backward(grads[f"dA{l+1}"], current_cache, "relu")

    return grads



def linear_activation_backward(dA, cache, activation):
    dA_prev, dZ, dW, db = None, None, None, None

    linear_cache, activation_cache = cache
    
    if activation == "relu":
        dZ = relu_backward(dA, activation_cache)
    elif activation == "sigmoid":
        dZ = sigmoid_backward(dA, activation_cache)

    da_prev, dW, db = linear_backward(dZ, linear_cache)
    return da_prev, dW, db


def linear_backward(dZ, linear_cache):
    m = dZ.shape[1]
    dW = (1 / m) * np.dot(dZ, linear_cache["A"].T)
    db = (1 / m) * np.sum(dZ, axis=1, keepdims=True)
    dA_prev = np.dot(linear_cache["W"].T, dZ)
    return dA_prev, dW, db

    

def sigmoid_backward(dAL, activation_cache):
    dZL = dAL * sigmoid_deriv(activation_cache["Z"])
    return dZL


def relu_backward(dA, activation_cache):
    dZ = dA * relu_deriv(activation_cache["Z"])
    return dZ


def sigmoid_deriv(Z):
    return sigmoid(Z) * (1 - sigmoid(Z))


def relu_deriv(Z):
    return np.where(Z >= 0, 1, 0)

    






def forward_propagation(X, parameters):
    caches = []
    A = X
    L = len(parameters) // 2

    for i in range(1, L):
        A_prev = A
        A, cache = linear_activation_forward(A_prev, parameters[f"W{i}"], parameters[f"b{i}"], "relu")
        caches.append(cache)

    AL, cache = linear_activation_forward(A, parameters[f"W{L}"], parameters[f"b{L}"], "sigmoid")
    caches.append(cache)
    return AL, caches


def linear_activation_forward(A, W, b, activation):
    cache = None
    Z, linear_cache = linear_forward(A, W, b)
    
    if activation == "relu":
        A, activation_cache = relu_forward(Z)
        cache = (linear_cache, activation_cache)
    elif activation == "sigmoid":
        A, activation_cache = sigmoid_forward(Z)
        cache = (linear_cache, activation_cache)

    return A, cache


def linear_forward(A, W, b):
    Z = np.dot(W, A) + b
    linear_cache = {"A": A, "W": W, "b": b}
    return Z, linear_cache


def relu_forward(Z):
    activation_cache = {"Z": Z}
    # return np.maximum(0, Z), activation_cache
    return Z * (Z > 0), activation_cache

def sigmoid_forward(Z):
    activation_cache = {"Z": Z}
    return sigmoid(Z), activation_cache

def sigmoid(Z):
    return expit(Z)








def update_parameters(parameters, gradients, learning_rate, reg_param):
    L = len(parameters) // 2
    m = parameters["W1"].shape[1]

    for i in range(1, L+1):
        reg_term = (reg_param / m) * parameters[f"W{i}"]
        parameters[f"W{i}"] -= learning_rate * (gradients[f"dW{i}"] + reg_term)
        parameters[f"b{i}"] -= learning_rate * gradients[f"db{i}"]










def compute_cost(AL, y, parameters, reg_param):
    m = AL.shape[1]
    epsilon = 1e-10
    reg_term = regularize_cost(parameters, m, reg_param)
    cost = -(1 / m) * np.sum(y * np.log(AL + epsilon) + (1 - y) * np.log(1 - AL + epsilon))
    return cost + reg_term
    


def regularize_cost(parameters, m, reg_param):
    L = len(parameters) // 2
    temp = 0
    for i in range(1, L+1):
        temp += np.sum(parameters[f"W{i}"]**2)

    return (reg_param / (2 * m)) * temp



def compute_accuracy(X, y, parameters):
    AL, caches = forward_propagation(X, parameters)
    y_pred = np.where(AL >= 0.5, 1, 0)

    comparison = np.where(y_pred == y, 1, 0)
    return np.sum(comparison) / y.shape[1]
