#!/usr/bin/env python

import argparse
import subprocess
import gzip
import time
import logging
import nltk
import pickle
import random
from nltk.tokenize.punkt import PunktWordTokenizer


def sequences(corpus):
    result = []
    for sentence in corpus:
        result.append([(part, '') for part in sentence])
    return result


def symbols(corpus):
    result = set()
    for sentence in corpus:
        result.update(sentence)
    return list(result)


def sample(hmm, length):
    sample = hmm.random_sample(random.Random(), length)
    sentence = ' '.join(t[0] for t in sample)
    return sentence


def save_model(filename, hmm):
    try:
        with gzip.GzipFile(filename, 'wb') as f:
            f.write(pickle.dumps(hmm, 1))
    except:
        logging.exception('save model failure')
        raise


def load_model(filename):
    try:
        with gzip.GzipFile(filename, 'rb') as f:
            buf = ''
            while True:
                data = f.read()
                if data == '':
                    break
                buf += data
            return pickle.loads(buf)
    except:
        logging.exception('load model failure')
    return None


def cleanup_words(words):
    exclude = [',', '.', '!', '@', '"', ';', "'", '?', '-', '--', ']', '[', ':', '/', '#', 'http',
               '(', ')', '*', '<', '>']
    return [word for word in words if not any(e in word for e in exclude)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--model', '-m', metavar='MODEL', type=str, nargs='?')
    group.add_argument('--corpus', '-c', metavar='CORPUS', type=str, nargs='?')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--speak', '-s', action='store_true')
    args = parser.parse_args()

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level)

    if args.model:
        logging.debug('loading model...')
        hmm = load_model(args.model)

    if args.corpus:
        logging.debug('loading corpus...')
        corpus = open(args.corpus, 'rb').read()
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        word_detector = PunktWordTokenizer()
        sentences = sent_detector.tokenize(corpus.strip())
        words = [cleanup_words(word_detector.tokenize(s)) for s in sentences]

        logging.debug('training model...')
        trainer = nltk.tag.hmm.HiddenMarkovModelTrainer(states=range(8), symbols=symbols(words))
        hmm = trainer.train_unsupervised(sequences(words), max_iterations=5)

        logging.debug('saving model...')
        save_model(args.corpus + '.hmm', hmm)

    logging.debug('sampling model...')

    while(True):
        utterance = sample(hmm, random.randint(5, 15)) + '.'
        print utterance
        if args.speak:
            subprocess.call('say "{}!"'.format(utterance), shell=True)
            time.sleep(1)
