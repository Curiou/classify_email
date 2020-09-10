# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    License: (C) Copyright 2018-2020, Shanghai hot nest network technology co. LTD.
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: network.py
    Time: 2020-09-10 18:54
    File Intro: 
"""
import tensorflow as tf
import tensorflow.keras as tk
import tensorflow.keras.layers as tl
from nip_classify.data_set_make import wordEmbeding
import numpy as np, pandas as pd
from config.CONFIG import NUM_WORDS, EMBEDDING_DIM, MAX_SEQUENCE_LENGTH, BATCH_SIZE, EPOCH
from config.CONFIG import DATASET_ONE_LABEL_DICT_REVERSE, DATASET_TWO_LABEL_DICT_REVERSE, DATASET_THREE_LABEL_DICT_REVERSE

# 统一网络参数数据类型
tf.keras.backend.set_floatx('float64')
from sklearn.metrics import recall_score, accuracy_score, f1_score

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)


def TrainOne():
    train_x, train_y = wordEmbeding(dataset=3, train=True)
    train_x = tf.convert_to_tensor(train_x, dtype=tf.float64)
    train_y = tf.convert_to_tensor(train_y, dtype=tf.float64)
    # dataset为3的时候才有fileName参数
    test_x, test_y, fileName = wordEmbeding(dataset=3, train=False)
    # test_x, test_y = wordEmbeding(dataset=2, train=False)
    test_x = tf.convert_to_tensor(test_x, tf.float64)
    test_y = tf.convert_to_tensor(test_y, tf.float64)

    model = tk.models.Sequential()
    '''
    embedding层见：
    https://tensorflow.google.cn/api_docs/python/tf/keras/layers/Embedding
    '''
    model.add(tk.layers.Embedding(input_dim=NUM_WORDS,
                                  output_dim=EMBEDDING_DIM,
                                  input_length=MAX_SEQUENCE_LENGTH
                                  ))
    # 此层输出数据shape为 (batch_size, imput_length, output_dim)
    model.add(tk.layers.Flatten())
    model.add(tk.layers.Dropout(0.3))
    model.add(tk.layers.Dense(100, activation='relu'))
    model.add(tk.layers.Dropout(0.2))
    model.add(tk.layers.Dense(150, activation='relu'))
    model.add(tk.layers.Dense(100, activation='relu'))
    model.add(tk.layers.Dropout(0.4))
    model.add(tk.layers.Dense(20, activation='softmax'))
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    model.fit(train_x, train_y,
              batch_size=BATCH_SIZE,
              epochs=EPOCH,
              validation_split=0.2
              )
    model.evaluate(test_x, test_y)
    test_y = np.array(test_y)
    print("===: ", test_y)
    a = model.predict(test_x)
    # print("+++"*22)
    # print(a)
    # print(a.shape)
    # print("+++" * 22)
    # 延轴1取最大值下标，即预测标签值
    pred = a.argmax(1)
    # print(pred)
    # print("+++" * 22)
    # print(test_y)
    print("准确率：", accuracy_score(test_y, pred))
    print("召回率： ", recall_score(test_y, pred, average="macro"))
    print("f1_score: ", f1_score(test_y, pred, average="weighted"))
    '''
    这后面仅是处理数据集3的时候才用
    '''
    # pre = [DATASET_THREE_LABEL_DICT_REVERSE[num] for num in pred]
    # tru = [DATASET_THREE_LABEL_DICT_REVERSE[num] for num in test_y]
    # print("==="*22)
    # print("pre length: ",len(pre))
    # print("true length: ", len(tru))
    # print("fileName: ", len(fileName))
    #
    # df = pd.DataFrame({"PredictionLable":pre, "TrueLable": tru, "fileName":fileName})
    # df.to_csv(r"C:\Users\Fisheep\Desktop\Code\py\Email\Dataset\DataframeHdf5\data33.csv", index= 0)
    # print(df.loc[:40, :])


'''
这种更灵活
'''


class MyModel(tk.Model):
    def __init__(self):
        super(MyModel, self).__init__()
        # 转换数据和标签成tensor
        # train 构造数据集，打乱，采样
        self.train_x, self.train_y = wordEmbeding()
        self.train_x = tf.convert_to_tensor(self.train_x, tf.float64)
        self.train_y = tf.convert_to_tensor(self.train_y, tf.int8)
        self.train_ds = tf.data.Dataset.from_tensor_slices((self.train_x, self.train_y)).shuffle(3000).batch(BATCH_SIZE)
        # test 构造数据集，打乱，采样
        self.test_x, self.test_y = wordEmbeding(train=False)
        self.test_x = tf.convert_to_tensor(self.test_x, tf.float64)
        self.test_y = tf.convert_to_tensor(self.test_y, tf.int8)
        self.test_ds = tf.data.Dataset.from_tensor_slices((self.test_x, self.test_y)).shuffle(3000).batch(BATCH_SIZE)

        # 构造网络
        # 此层输出数据shape为 (batch_size, imput_length, output_dim)
        self.embedding = tl.Embedding(input_dim=NUM_WORDS,
                                      output_dim=EMBEDDING_DIM,
                                      input_length=MAX_SEQUENCE_LENGTH)
        self.flatten1 = tl.Flatten()
        self.d1 = tl.Dense(64, activation='relu')
        self.drop1 = tl.Dropout(0.2)
        self.d2 = tl.Dense(128, activation='relu')
        self.drop2 = tl.Dropout(0.3)
        self.d3 = tl.Dense(20, activation='softmax')

    def call(self, inputs):
        x = self.embedding(inputs)
        x = self.flatten1(x)
        x = self.d1(x)
        x = self.drop1(x)
        x = self.d2(x)
        x = self.d3(x)
        return x

    def train(self, model):
        # 损失函数和优化器
        loss_fun = tk.losses.SparseCategoricalCrossentropy()
        # optimizer = tk.optimizers.Adam()
        optimizer = tk.optimizers.RMSprop()

        # 训练集平均损失函数和准确率
        train_loss = tk.metrics.Mean(name='train_loss')
        train_accuracy = tk.metrics.SparseCategoricalAccuracy(name='train_accuracy')

        # 测试集平均损失函数和准确率
        test_loss = tk.metrics.Mean(name='test_loss')
        test_accuracy = tk.metrics.SparseCategoricalAccuracy(name='test_accuracy')
        # 打印模板
        test_template = 'EPOCH--->{}, test_loss--->{}, test_acc--->{}'
        train_template = 'EPOCH--->{}, trainBatch_loss--->{}, trainBatch_acc--->{}'

        @tf.function
        def test_step(data, labels):
            prediction = model(data)
            loss = loss_fun(labels, prediction)
            test_loss(loss)
            test_accuracy(labels, prediction)

        @tf.function
        def train_step(data, labels):
            with tf.GradientTape() as tape:
                prediction = model(data)
                loss = loss_fun(labels, prediction)
            gradient = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(gradient, model.trainable_variables))

            # 获取批损失和准确率
            train_loss(loss)
            train_accuracy(labels, prediction)

        for epoch in range(EPOCH):
            for data, labels in self.train_ds:
                train_step(data=data, labels=labels)
            # 每轮打印一次训练结果
            print(train_template.format(epoch + 1,
                                        train_loss.result(),
                                        train_accuracy.result()))
            # 每轮测试一次并打印测试结果
            for test_data, test_labels in self.test_ds:
                test_step(test_data, test_labels)
            print(test_template.format(epoch + 1,
                                       test_loss.result(),
                                       test_accuracy.result()))


def train():
    # 构建模型开始训练
    model = MyModel()
    model.train(model=model)


if __name__ == '__main__':
    TrainOne()
    # 两种方法，下面这种更灵活一点
    # train()
