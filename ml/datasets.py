def get_mnist():
    """
    retrieves the mnist dataset using keras
    input::
        None
    return::
        data (tuple): (train_data,train_label), (test_data,test_labels)
    """
    from keras.datasets import mnist
    return mnist.load_data()

def get_fashion_mnist():
    """
    retrieves the fashion_mnist dataset using keras
    input::
        None
    return::
        data (tuple): (train_data,train_label), (test_data,test_labels)
    """
    from keras.datasets import fashion_mnist
    fashion_mnist.load_data()


def get_cifar10():
    """
    retrieves the cifar10 dataset using keras
    input::
        None
    return::
        data (tuple): (train_data,train_label), (test_data,test_labels)
    """
    from keras.datasets import cifar10
    return cifar10.load_data()

def get_cifar100(fine=True):
    """
    retrieves the cifar100 dataset using keras
    input::
        fine (bool) = True:
                whether or not to load the fine or coarse labels
    return::
        data (tuple): (train_data,train_label), (test_data,test_labels)
    """
    from keras.datasets import cifar100
    if fine:
        label_mode = 'fine'
    else:
        label_mode = 'coarse'
    cifar100.load_data()
