def levenshtein_distance(statement, other_statement):
    from fuzzywuzzy import fuzz

    return fuzz.ratio(statement.text.lower(), other_statement.text.lower())


def synset_distance(statement, other_statement):
    """
    Calculate the similarity of two statements.
    This is based on the total similarity between
    each word in each sentence.
    """
    from chatterbot.utils.pos_tagger import POSTagger
    from chatterbot.utils.stop_words import StopWordsManager
    from chatterbot.utils.word_net import Wordnet
    import itertools

    wordnet = Wordnet()
    tagger = POSTagger()
    stopwords = StopWordsManager()

    def get_tokens(text, exclude_stop_words=True):
        """
        Takes a string and converts it to a tuple
        of each word. Skips common stop words such
        as ("is, the, a, ...") is 'exclude_stop_words'
        is True.
        """
        lower = text.lower()
        tokens = tagger.tokenize(lower)

        # Remove any stop words from the string
        if exclude_stop_words:
            excluded_words = stopwords.words('english')

            tokens = set(tokens) - set(excluded_words)

        return tokens

    tokens1 = get_tokens(statement.text)
    tokens2 = get_tokens(other_statement.text)

    total_similarity = 0

    # Get the highest matching value for each possible combination of words
    for combination in itertools.product(*[tokens1, tokens2]):

        synset1 = wordnet.synsets(combination[0])
        synset2 = wordnet.synsets(combination[1])

        if synset1 and synset2:

            max_similarity = 0

            # Get the highest similarity for each combination of synsets
            for synset in itertools.product(*[synset1, synset2]):
                similarity = synset[0].path_similarity(synset[1])

                if similarity and (similarity > max_similarity):
                    max_similarity = similarity

            # Add the most similar path value to the total
            total_similarity += max_similarity

    return total_similarity


def jaccard_similarity(a, b, threshold=0.5):
    a = a.text
    b = b.text
    """
    The Jaccard index is composed of a numerator and denominator.
    In the numerator, we count the number of items that are shared between the sets.
    In the denominator, we count the total number of items across both sets.
    Let's say we define sentences to be equivalent if 50% or more of their tokens are equivalent.
    Here are two sample sentences:

        The young cat is hungry.
        The cat is very hungry.

    When we parse these sentences to remove stopwords, we end up with the following two sets:

        {young, cat, hungry}
        {cat, very, hungry}

    In our example above, our intersection is {cat, hungry}, which has count of two.
    The union of the sets is {young, cat, very, hungry}, which has a count of four.
    Therefore, our Jaccard similarity index is two divided by four, or 50%.
    Given our threshold above, we would consider this to be  a match
    """
    from nltk.corpus import wordnet
    import nltk.corpus
    import nltk
    import string

    # Get default English stopwords and extend with punctuation
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(string.punctuation)
    stopwords.append('')
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

    def get_wordnet_pos(pos_tag):
        if pos_tag[1].startswith('J'):
            return (pos_tag[0], wordnet.ADJ)
        elif pos_tag[1].startswith('V'):
            return (pos_tag[0], wordnet.VERB)
        elif pos_tag[1].startswith('N'):
            return (pos_tag[0], wordnet.NOUN)
        elif pos_tag[1].startswith('R'):
            return (pos_tag[0], wordnet.ADV)
        else:
            return (pos_tag[0], wordnet.NOUN)

    ratio = 0
    pos_a = map(get_wordnet_pos, nltk.pos_tag(nltk.tokenize.word_tokenize(a)))
    pos_b = map(get_wordnet_pos, nltk.pos_tag(nltk.tokenize.word_tokenize(b)))
    lemmae_a = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a \
                    if pos == wordnet.NOUN and token.lower().strip(string.punctuation) not in stopwords]
    lemmae_b = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b \
                    if pos == wordnet.NOUN and token.lower().strip(string.punctuation) not in stopwords]

    # Calculate Jaccard similarity
    try:
        ratio = len(set(lemmae_a).intersection(lemmae_b)) / float(len(set(lemmae_a).union(lemmae_b)))
    except Exception as e:
        print('Error', e)
    return (ratio >= threshold)
