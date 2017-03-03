import tflearn


def inception_v4_2d(input_tensor=[None, 512], output_tensor=[None, 1]):
    """
    Generates an inception model that conforms to specified input/output tensors.
    :param input_tensor: Dimensions of input
    :param output_tensor: Dimensions of output
    :return: An instance of tflearn.DNN class supporting {fit, predict, evaluate, save, load} methods
    """
    raise NotImplementedError


def inception_v4_3d(input_tensor=[None, 512], output_tensor=[None, 1]):
    """
    Generates an inception model that conforms to specified input/output tensors.
    :param input_tensor: Dimensions of input
    :param output_tensor: Dimensions of output
    :return: An instance of tflearn.DNN class supporting {fit, predict, evaluate, save, load} methods
    """
    raise NotImplementedError