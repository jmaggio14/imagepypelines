# imsciutils tutorials

## building your own pipeline
Pipelines are constructed of `blocks` which are simply objects that take in data,
process it, and output the processed data

![pipeline](https://github.com/jmaggio14/imsciutils/blob/develop/docs/images/pipeline-example.png "pipeline example")

#### let's create an example pipeline using blocks that are built into imsciutils
```python

```

### Machine Learning Applications
One of the more powerful applications of `imsciutils` is it's ease of use in
_machine learning_ and _feature engineering_ applications. We can easily build
a simple image classifier that is tailored to your purposes

```python
import imsciutils as iu

features = iu.PretrainedNetwork() # generate image features
pca = iu.PCA(256) # apply principle component analysis to input features
neural_network = iu.MultilayerPerceptron(neurons=512) # neural network classifier
# there are a lot more parameters you can tweak!

classifier = iu.Pipeline([features,pca,neural_network])

# for this example, we'll need to load the standard Mnist handwriting dataset
# built into `imsciutils`
mnist = iu.Mnist()
train_data, train_labels = mnist.get_train()
test_data, ground_truth = mnist.get_test()

# train the classifier
classifier.train(train_data,train_labels)

# test the classifier
predictions = classifier.process(test_data)

# print the accuracy
accuracy = iu.accuracy(predictions,ground_truth)
print(accuracy)
```
