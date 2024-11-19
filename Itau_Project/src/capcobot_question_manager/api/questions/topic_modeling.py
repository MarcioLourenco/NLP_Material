import gensim
import gensim.corpora as corpora
import nltk
import spacy

from src.capcobot_question_manager.utils.language_utils import (
    get_default_language,
    get_language,
)


def lemmatization(
    text, allowed_postags=["NOUN"], language=get_default_language()["spacy"]
):
    nlp = spacy.load(language, disable=["parser", "ner"])
    doc = nlp(text)
    new_text = []
    for token in doc:
        if token.pos_ in allowed_postags:
            new_text.append(token.lemma_)
    return new_text


def gen_words(texts):
    final = []
    for text in texts:
        new = gensim.utils.simple_preprocess(text, deacc=True)
        final.append(new)
    return final


def remove_stopwords(texts, language):
    nltk.download("stopwords", quiet=True)
    stopwords = nltk.corpus.stopwords.words(language)
    final = []
    for doc in texts:
        new_words = []
        for word in doc:
            if word not in stopwords:
                new_words.append(word)
        final.append(new_words)
    return final


def get_corpus_id2word(texts):
    id2word = corpora.Dictionary(texts)
    corpus = []
    for text in texts:
        new = id2word.doc2bow(text)
        corpus.append(new)
    return corpus, id2word


def get_topics(message, language_param):
    message = message.replace(".", "").replace("_", "").lower()
    if len(message.strip()) == 0:
        return None

    lemmatized_message = lemmatization(
        message,
        get_language(language_param["language"])["part_of_speech"],
        language_param["spacy"],
    )

    if len(lemmatized_message) > 0:
        data_words = gen_words(lemmatized_message)
        data_words = remove_stopwords(data_words, language_param["nltk"])
        corpus, id2word = get_corpus_id2word(data_words)

        # LDA model
        lda_model = gensim.models.ldamodel.LdaModel(
            corpus=corpus,
            id2word=id2word,
            num_topics=5,
            random_state=100,
            update_every=1,
            chunksize=100,
            passes=10,
            alpha="auto",
        )
        topic = lda_model[corpus][0]
        best_topic = sorted(topic, key=lambda x: (x[1]), reverse=True)[0]
        topic_num = best_topic[0]

        wp = lda_model.show_topic(topic_num)
        topic_keywords = [word for word, prop in wp]
        return topic_keywords
    else:
        return None
