# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Conglin Du
    License: (C) Copyright 2018-2020, Shanghai hot nest network technology co. LTD.
    Contact: gduxiansheng@gmail.com or 2544284522@qq.com
    File: data_set_make.py
    Time: 2020-09-10 18:47
    File Intro: 
"""
import pandas as pd, numpy as np
import re
import jieba

from astropy.io.misc.tests.test_pandas import pandas
from nltk.corpus import stopwords

'''
若有错，则运行时按照错误提示下载stopwords即可
'''
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os
from config.CONFIG import NUM_WORDS, MAX_SEQUENCE_LENGTH, EMBEDDING_DIM
# 数据集1的，导入标签对应关系，训练集和测试集的目录，h5的保存路径
from config.CONFIG import DATASET_ONE_LABEL_DICT, TRAIN_ROOT_DIR, TEST_ROOT_DIR, TRAIN_H5_PATH, TEST_H5_PATH
# 数据集2的，导入标签对应关系，训练集和测试集的目录，h5的保存路径
from config.CONFIG import DATASET_TWO_LABEL_DICT, TWO_TRAIN_ROOT_PATH, TWO_TEST_ROOT_PATH, TWO_TRAIN_H5_PATH, \
    TWO_TEST_H5_PATH
# 数据集3的，导入标签对应关系，训练集目录，h5的保存路径
from config.CONFIG import DATASET_THREE_LABEL_DICT, THREE_TRAIN_ROOT_PATH, THREE_TEST_ROOT_PATH, THREE_TRAIN_H5_PATH, \
    THREE_TEST_H5_PATH
# 加载停止词
from config.CONFIG import STOP_WORDS_FILE_PATH


def dataset2(dataset, train=True):
    """
    处理数据集2，3
    :parameters:
        dataset,值为2或3，表示第几个数据集
        train，默认为true，表示是训练集还是测试集
    1.按目录读取，将一个train或者test的打上标签分别制作成对应的DataFrame
    2.将这个DataFrame进行分词，去停用词，最后保存成H5
    :return:
    """
    if dataset == 2:
        label_map = DATASET_TWO_LABEL_DICT
        if train == True:
            rootDir = TWO_TRAIN_ROOT_PATH
            hdf5SavePath = TWO_TRAIN_H5_PATH
        else:
            rootDir = TWO_TEST_ROOT_PATH
            hdf5SavePath = TWO_TEST_H5_PATH
    elif dataset == 3:
        label_map = DATASET_THREE_LABEL_DICT
        if train:
            rootDir = THREE_TRAIN_ROOT_PATH
            hdf5SavePath = THREE_TRAIN_H5_PATH
        else:
            rootDir = THREE_TEST_ROOT_PATH
            hdf5SavePath = THREE_TEST_H5_PATH

    def is_chinese(uchar):
        # 判断一个unicode是否是汉字
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return True
        else:
            return False

    def format_str(content):
        """
        1.仅保留句子里面的中文，去掉其余一切符号
        2.jieba分词
        :param content: 待处理字符串
        :return: 经过jieba分词之后的，去掉停止词的以空格连接的一个字符串
        """
        content_str = ''
        for i in content:
            if is_chinese(i):
                content_str = content_str + i
        # jieba分词，去停用词，并用空格连接
        return ' '.join([word for word in (jieba.cut(content_str)) if word not in stop_words_list])

    def stopwordslist(filepath):
        """
        读取停用词txt，创建停用词list
        """
        stopwords = [line.decode('utf-8').strip() for line in open(filepath, 'rb').readlines()]
        return stopwords

    def read_root_dir(rootDir):
        """
        遍历目录，将训练集或测试集数据带他们的标签一起，制作成一个DataFrame
        :param rootDir: 总目录
        :return: 返回制作好的dataframe
        """
        DataFrame = pd.DataFrame(columns=['content', 'label', 'fileName'])
        # 获取文件下的子目录
        subDirs = os.listdir(rootDir)
        for subDir in subDirs:
            # 转换标签
            label = subDir
            for file in os.listdir(os.path.join(rootDir, subDir)):
                # 构造文件路径
                singleFilePath = os.path.join(rootDir, subDir, file)
                print('Now processing-----', singleFilePath)
                with open(singleFilePath, encoding="utf8") as f:
                    content_str = f.read()
                DataFrame = DataFrame.append(pd.DataFrame({'content': [content_str], 'label': [label]}),
                                             ignore_index=True)
                # 这里当是制作数据集3（学科数据那个）时才用，因为后面要记录是哪个文件的预测，所以这里要加一列filename
                # DataFrame = DataFrame.append(pd.DataFrame({'content': [content_str], 'label': [label], 'fileName': [file]}), ignore_index=True)
        return DataFrame

    # 加载停止词
    stop_words_list = stopwordslist(STOP_WORDS_FILE_PATH)
    # 制作df
    DF = read_root_dir(rootDir=rootDir)
    print(DF)
    print("-----------------------------正在分词，此过程最长约15分钟-------------------------------------")
    # 编码标签
    DF["label"] = DF['label'].map(label_map)
    # 保留中文并且经过jieba分词
    DF["content"] = DF['content'].apply(format_str)
    # print(DF)
    # 打乱数据
    DF = DF.sample(frac=1).reset_index(drop=True)
    print(DF)
    DF.to_hdf(hdf5SavePath, key='df', mode='w')
    print("-----------------------------    保存成功    -------------------------------------")


def processSingleFile(singleFilePath):
    '''
    仅处理数据集1
    :param singleFilePath:
    :return:
    '''
    # 参数error_bad_lines：跳过文件内出错的行
    singleDataFrame = pd.read_table(singleFilePath, header=None, encoding='utf8', engine='python',
                                    error_bad_lines=False)

    singleDataFrame.columns = ['content']

    # print(singleDataFrame)
    # print('=====================')

    def pre_clean_text(origin_text):
        # 去掉标点符号和非法字符
        origin_text = str(origin_text)
        text = re.sub('[^a-zA-Z]', ' ', origin_text)
        # 将字符全部转化为小写，并通过空格符进行分词处理,split()默认空格分开
        words = text.lower().split()
        # 去停用词
        stop_words = set(stopwords.words("english"))
        meaningful_words = [w for w in words if w not in stop_words]
        # 将剩下的词还原成str类型
        # 用空格连接列表变为string
        cleaned_text = " ".join(meaningful_words)
        return cleaned_text

    # 清理数据
    singleDataFrame['content'] = singleDataFrame['content'].apply(lambda x: pre_clean_text(x))
    # 压缩空维度
    valueList = np.squeeze(singleDataFrame.values)
    # print(valueList)
    # valueList = [valueList.pop(i) for i in range(len(valueList) - 1) if valueList[i] == '']

    # print('++++++++')
    # print(valueList)
    # print(' '.join(np.squeeze(singleDataFrame.values)))
    # print(valueList)
    validSentence = ' '.join(valueList)
    # print('end---------------------------')
    # print(validSentence)
    return validSentence


def makeDataFrame(train=True):
    '''
    仅用于数据集1的制作
    :param train: 构建训练集还是测试集，默认true代表训练集
    :return: void 无返回值，直接将全部数据的DataFrame持久化为h5文件，
    '''
    DataFrame = pd.DataFrame(columns=['content', 'label'])
    # 根据操作的是train还是test更改目录
    if train:
        print('=================train==================')
        rootDir = TRAIN_ROOT_DIR
        hdf5SavePath = TRAIN_H5_PATH
    else:
        print('=================test==================')
        rootDir = TEST_ROOT_DIR
        hdf5SavePath = TEST_H5_PATH
    # os.chdir(rootDir)
    # 获取文件下的子目录
    subDirs = os.listdir(rootDir)
    # 记录对应异常个数
    j, k, h = 0, 0, 0
    for subDir in subDirs:
        # 转换标签
        label = DATASET_ONE_LABEL_DICT[subDir]
        for file in os.listdir(os.path.join(rootDir, subDir)):
            # 构造文件路径
            singleFilePath = os.path.join(rootDir, subDir, file)
            print('Now processing-----', singleFilePath)
            # 捕获异常，异常过多可添加处理，我这里仅是记录文件处理异常的文件个数
            try:
                # 对每个文件进行处理，返回的该文件内容有效字符构成的字符串
                sentence = processSingleFile(singleFilePath=singleFilePath)
            except pandas.errors.ParserError as e:
                j += 1
                continue
            except UnicodeDecodeError as e1:
                k += 1
                continue
            except ValueError as e2:
                h += 1
                continue
            # 添加至DataFrame里
            DataFrame = DataFrame.append(pd.DataFrame({'content': [sentence], 'label': [label]}), ignore_index=True)
    # 显示因异常未读取的文件个数
    print('pandas.errors.ParserError missed--->', j, '  UnicodeDecodeError missed--->', k, '   ValueError--->', h)
    # 打乱顺序并以覆盖的方式存储成h5文件
    DataFrame = DataFrame.sample(frac=1).reset_index(drop=True)
    DataFrame.to_hdf(hdf5SavePath, key='df', mode='w')

    print(DataFrame.head(5))
    print(DataFrame['label'].unique())
    # 统计标签种类
    print(DataFrame['label'].nunique())


def wordEmbeding(dataset, train=True):
    '''
    :param dataset: 使用的数据集编号
    :param train: 训练还是测试数据集
    :return: 对于1，2数据集，返回data，label；
            对于数据集3，返回data，label，fileName；
    '''
    train_h5_path = None
    test_h5_path = None
    # 判断是处理的那个数据集
    if dataset == 1:
        train_h5_path = TRAIN_H5_PATH
        test_h5_path = TEST_H5_PATH
    elif dataset == 2:
        train_h5_path = TWO_TRAIN_H5_PATH
        test_h5_path = TWO_TEST_H5_PATH
    elif dataset == 3:
        # Dataset3只有训练集没有测试集
        train_h5_path = THREE_TRAIN_H5_PATH
        test_h5_path = THREE_TEST_H5_PATH
    '''
    向量化文本，将文本转化为向量序列
    Tokenizer参数用法及含义见：
    https://tensorflow.google.cn/api_docs/python/tf/keras/preprocessing/text/Tokenizer
    :param train: 对训练集还是测试集操作，默认训练集
    :return:制作好的序列数据和对应标签np数组
    '''
    tokenizer = Tokenizer(num_words=NUM_WORDS)
    DataFrame = pd.read_hdf(train_h5_path)
    # 训练
    # 这里一定是用训练集的来训练
    tokenizer.fit_on_texts(DataFrame.content)
    # 如果是测试集的话还需要读测试h5进行覆盖
    if not train:
        DataFrame = pd.read_hdf(test_h5_path)

    # 将文本列表转换为序列，一个文本对应一个序列
    sequence = tokenizer.texts_to_sequences(DataFrame.content)
    # word_idnex = tokenizer.word_index
    # data = tokenizer.sequences_to_matrix(sequence)
    # data = tokenizer.texts_to_matrix(DataFrame.content)
    # 为序列进行填充，以0填充
    data = pad_sequences(sequences=sequence, maxlen=MAX_SEQUENCE_LENGTH)
    print(data)
    print('================')
    label = DataFrame['label'].values
    print('data.shape--->', data.shape, '   data type--->', type(data))
    print('label shape--->', label.shape, '  label type--->', type(label))
    if dataset == 3 and train == False:
        return data, label, DataFrame['fileName'].values
    else:
        return data, label


if __name__ == '__main__':
    pass
    # dataset2(dataset= 3, train= True)
    dataset2(dataset=3, train=False)
    # makeDataFrame(train= False)   #测试集
    # makeDataFrame()   #训练集
    # wordEmbeding(train= False)    #测试集
    # wordEmbeding()  #训练集
