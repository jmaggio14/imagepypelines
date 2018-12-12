


def test_SimpleImageClassifier():
    """
    this runs a short training session and runs data throught it.
    it does NOT test the accuracy of such a model, because training it would take
    far too long
    """
    import imagepypelines as ip

    # get data subsample
    cifar10 = ip.ml.Cifar10()
    x_train_base, y_train_base = cifar10.get_train()
    x_test_base, ground_truth_base = cifar10.get_test()

    x_train, y_train = ip.xysample(x_train_base, y_train_base,.01)
    x_test, ground_truth = ip.xysample(x_test_base, ground_truth_base,.01)

    classifier = ip.pipelines.SimpleImageClassifier().debug()
    classifier.train(x_train,y_train)

    predicted = classifier.process(x_test)
    accuracy = ip.accuracy(predicted,ground_truth)
