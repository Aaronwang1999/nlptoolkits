import seminlpclassify.qihangfuncs
from . import _dictionary
from . import nlp_models
from . import _file_util
from . import preprocess
from . import preprocess_parallel
from . import scorer
from . import qihangfuncs
# out source pack
import functools
import datetime
import itertools
import os
import pathos
import stanfordnlp.server
import gensim
import typing
import shutil

"""Other functions"""


def delete_whole_dir(directory):
    """delete the whole dir..."""
    if os.path.exists(directory) and os.path.isdir(directory):
        shutil.rmtree(directory)


"""Process file"""


def process_largefile(
        path_input_txt,
        path_output_txt,
        input_index_list,
        path_output_index_txt,
        process_line_func,
        chunk_size=100,
        start_iloc=None,
):
    """ A helper function that transforms an input_data file + a list of IDs of each line (documents + document_IDs)
    to two output files (processed_data documents + processed_data document IDs)
    by calling function_name on chunks of the input_data files.
      Each document can be decomposed into multiple processed_data documents (e.g. sentences).
      Not support Multiprocessor


    Arguments:
    :param path_input_txt:  {str or Path} path to a text file, each line is a document
    :param path_output_txt: {str or Path} processed_data linesentence file (remove if exists)
    :param input_index_list: {str} -- a list of input_data line ids
    :param path_output_index_txt: {str or Path} -- path to the index file of the output
    :param process_line_func: {callable} -- A function that processes a list of strings, list of ids and return
        a list of processed_data strings and ids. func(line_text, line_ids)
    :param chunk_size: {int} -- number of lines to process each time, increasing the default may increase performance
    :param start_iloc: {int} -- line number to start from (index starts with 0)

    Writes:
        Write the ouput_file and output_index_file

      Not support Multiprocessor
    """

    # check data must save in txt and dim be 1:

    try:
        if start_iloc is None:
            # if start from the first line, remove existing output file
            # else append to existing output file
            os.remove(str(path_output_txt))
            os.remove(str(path_output_index_txt))
    except OSError:
        pass
    assert _file_util.line_counter(path_input_txt) == len(
        input_index_list
    ), "Make sure the input_data file has the same number of rows as the input_data ID file. "

    with open(path_input_txt, newline="\n", encoding="utf-8", errors="ignore") as f_in:
        line_i = 0
        # jump to index
        if start_iloc is not None:
            # start at start_index line
            for _ in range(start_iloc):
                next(f_in)
            input_index_list = input_index_list[start_iloc:]
            line_i = start_iloc
        for next_n_lines, next_n_line_ids in zip(
                itertools.zip_longest(*[f_in] * chunk_size),
                itertools.zip_longest(*[iter(input_index_list)] * chunk_size),
        ):
            line_i += chunk_size
            print(datetime.datetime.now())
            print(f"Processing line: {line_i}.")
            next_n_lines = list(filter(None.__ne__, next_n_lines))
            next_n_line_ids = list(filter(None.__ne__, next_n_line_ids))
            output_lines = []
            output_line_ids = []
            # Use parse_parallel.py to speed things up
            for output_line, output_line_id in map(
                    process_line_func, next_n_lines, next_n_line_ids
            ):
                output_lines.append(output_line)
                output_line_ids.append(output_line_id)
            output_lines = "\n".join(output_lines) + "\n"
            output_line_ids = "\n".join(output_line_ids) + "\n"
            with open(path_output_txt, "a", newline="\n", encoding='utf-8') as f_out:
                f_out.write(output_lines)
            if path_output_index_txt is not None:
                with open(path_output_index_txt, "a", newline="\n", encoding="utf-8") as f_out:
                    f_out.write(output_line_ids)


def mp_process_largefile(
        path_input_txt,
        path_output_txt,
        input_index_list,
        path_output_index_txt,
        process_line_func,
        multiprocess_threads,
        chunk_size=100,
        start_iloc=None,

):
    """ A helper function that transforms an input_data file + a list of IDs of each line (documents + document_IDs)
    to two output files (processed_data documents + processed_data document IDs)
    by calling function_name on chunks of the input_data files.
      Each document can be decomposed into multiple processed_data documents (e.g. sentences).



    Arguments:
    :param path_input_txt:  {str or Path} path to a text file, each line is a document
    :param path_output_txt: {str or Path} processed_data linesentence file (remove if exists)
    :param input_index_list: {str} -- a list of input_data line ids
    :param path_output_index_txt: {str or Path} -- path to the index file of the output
    :param process_line_func: {callable} -- A function that processes a list of strings, list of ids and return
        a list of processed_data strings and ids. func(line_text, line_ids)
    :param multiprocess_threads: {int} -- the core to use, should be same as the argument of your project,
        like globaloption.NCORES
    :param chunk_size: {int} -- number of lines to process each time, increasing the default may increase performance
    :param start_iloc: {int} -- line number to start from (index starts with 0)

    Writes:
        Write the ouput_file and output_index_file
    """
    try:
        if start_iloc is None:
            # if start from the first line, remove existing output file
            # else append to existing output file
            os.remove(str(path_output_txt))
            os.remove(str(path_output_index_txt))
    except OSError:
        pass
    assert _file_util.line_counter(path_input_txt) == len(
        input_index_list
    ), "Make sure the input_data file has the same number of rows as the input_data ID file. "

    with open(path_input_txt, newline="\n", encoding="utf-8", errors="ignore") as f_in:
        line_i = 0
        # jump to index
        if start_iloc is not None:
            # start at start_index line
            for _ in range(start_iloc):
                next(f_in)
            input_index_list = input_index_list[start_iloc:]
            line_i = start_iloc
        for next_n_lines, next_n_line_ids in zip(
                itertools.zip_longest(*[f_in] * chunk_size),
                itertools.zip_longest(*[iter(input_index_list)] * chunk_size),
        ):
            line_i += chunk_size
            print(datetime.datetime.now())
            print(f"Processing line: {line_i}.")
            next_n_lines = list(filter(None.__ne__, next_n_lines))
            next_n_line_ids = list(filter(None.__ne__, next_n_line_ids))
            output_lines = []
            output_line_ids = []
            with pathos.multiprocessing.Pool(processes=multiprocess_threads,
                                             initializer=qihangfuncs.threads_interrupt_initiator
                                             ) as pool:
                for output_line, output_line_id in pool.starmap(
                        process_line_func, zip(next_n_lines, next_n_line_ids)
                ):
                    output_lines.append(output_line)
                    output_line_ids.append(output_line_id)
            output_lines = "\n".join(output_lines) + "\n"
            output_line_ids = "\n".join(output_line_ids) + "\n"
            with open(path_output_txt, "a", newline="\n", encoding='utf-8') as f_out:
                f_out.write(output_lines)
            if path_output_index_txt is not None:
                with open(path_output_index_txt, "a", newline="\n", encoding='utf-8') as f_out:
                    f_out.write(output_line_ids)


"""parser"""


def l1_auto_parser(
        endpoint,
        memory,
        nlp_threads,
        path_input_txt,
        path_output_txt,
        input_index_list,
        path_output_index_txt,
        chunk_size=100,
        start_iloc=None,
        use_multicores: bool = True,
        **kwargs):
    """
    :param memory: memory using, should be str like "\d+G"
    :param nlp_threads: how much threads does nlp use.
    :param endpoint: endpoint in stanfordnlp.server.CoreNLPClient, should be address of port
    :param path_input_txt:  {str or Path} path to a text file, each line is a document
    :param path_output_txt: {str or Path} processed_data linesentence file (remove if exists)
    :param input_index_list: {str} -- a list of input_data line ids
    :param path_output_index_txt: {str or Path} -- path to the index file of the output
    :param chunk_size: {int} -- number of lines to process each time, increasing the default may increase performance
    :param start_iloc: {int} -- line number to start from (index starts with 0)
    :param use_multicores: do you use multicores?

    Writes:
        Write the ouput_file and output_index_file

    """
    # supply for arguments
    kwargs['properties'] = kwargs['properties'] if 'properties' in kwargs else {
        "ner.applyFineGrained": "false",
        "annotators": "tokenize, ssplit, pos, lemma, ner, depparse",
    }
    kwargs['timeout'] = kwargs['timeout'] if 'timeout' in kwargs else 12000000
    kwargs['max_char_length'] = kwargs['max_char_length'] if 'max_char_length' in kwargs else 1000000

    def _lambda_process_line(line, lineID, corpus_processor):
        """Process each line and return a tuple of sentences, sentence_IDs,

        Arguments:
            line {str} -- a document
            lineID {str} -- the document ID

        Returns:
            str, str -- processed_data document with each sentence in a line,
                        sentence IDs with each in its own line: lineID_0 lineID_1 ...
        """
        try:
            sentences_processed, doc_sent_ids = corpus_processor.process_document(
                line, lineID
            )
            return "\n".join(sentences_processed), "\n".join(doc_sent_ids)
        except Exception as e:
            print(e)
            print("Exception in line: {}".format(lineID))

    with stanfordnlp.server.CoreNLPClient(
            memory=memory,
            threads=nlp_threads,
            endpoint=endpoint,  # must type in
            **kwargs
    ) as client:

        if use_multicores:
            """you must make corenlp and mp.Pool's port are same!!!"""
            mp_process_largefile(
                path_input_txt=path_input_txt,
                path_output_txt=path_output_txt,
                input_index_list=input_index_list,
                path_output_index_txt=path_output_index_txt,
                process_line_func=lambda x, y:
                # you must make corenlp and mp.Pool's port are same
                preprocess_parallel.process_document(x, y, endpoint),
                multiprocess_threads=nlp_threads,
                chunk_size=chunk_size,
                start_iloc=start_iloc
            )
        else:
            corpus_preprocessor = preprocess.preprocessor(client)

            process_largefile(
                path_input_txt=path_input_txt,
                path_output_txt=path_output_txt,
                input_index_list=input_index_list,
                path_output_index_txt=path_output_index_txt,
                process_line_func=lambda x, y: _lambda_process_line(x, y, corpus_preprocessor),
                chunk_size=chunk_size,
                start_iloc=start_iloc
            )


"""clean the parsed file"""


def l1_clean_parsed_txt(path_in_parsed_txt, path_out_cleaned_txt):
    """clean the entire corpus (output from CoreNLP) like l1_auto_parser

    Arguments:
        in_file {str or Path} -- input_data corpus, each line is a sentence
        out_file {str or Path} -- output corpus
    """
    a_text_clearner = preprocess.text_cleaner()
    process_largefile(
        path_input_txt=path_in_parsed_txt,
        path_output_txt=path_out_cleaned_txt,
        input_index_list=[
            str(i) for i in range(_file_util.line_counter(path_in_parsed_txt))
        ],  # fake IDs (do not need IDs for this function).
        path_output_index_txt=None,
        process_line_func=functools.partial(a_text_clearner.clean),
        chunk_size=200000,
    )


def l1_mp_clean_parsed_txt(path_in_parsed_txt, path_out_cleaned_txt, mp_threads=os.cpu_count()):
    """
    clean the entire corpus (output from CoreNLP), like l1_auto_parser
    could use "multiprocessing"

    Arguments:
        in_file {str or Path} -- input_data corpus, each line is a sentence
        out_file {str or Path} -- output corpus
    """
    a_text_clearner = preprocess.text_cleaner()
    mp_process_largefile(
        path_input_txt=path_in_parsed_txt,
        path_output_txt=path_out_cleaned_txt,
        input_index_list=[
            str(i) for i in range(_file_util.line_counter(path_in_parsed_txt))
        ],  # fake IDs (do not need IDs for this function).
        path_output_index_txt=None,
        process_line_func=functools.partial(a_text_clearner.clean),
        multiprocess_threads=mp_threads,
        chunk_size=200000,
    )


"""train and transform the model"""


def auto_bigram_fit_transform_txt(path_input_clean_txt,
                                  path_output_transformed_txt,
                                  path_output_model_mod,
                                  phrase_min_length: int,
                                  stopwords_set,
                                  threshold=None,
                                  scoring="original_scorer"
                                  ):
    """
    transform the sep two length words to concat in a word which join by '_'
    which means uni-gram -> bi-gram words.
    you can recursive this function to get the target tri-gram or bigger phrases.
    
    Args:
        path_input_clean_txt:
        path_output_transformed_txt:
        path_output_model_mod:
        phrase_min_length:
        stopwords_set:
        threshold:
        scoring:

    Returns:

    """

    # precheck
    if not str(path_output_model_mod).endswith('.mod'):
        raise ValueError('Model must end with .mod')

    # train and apply a phrase model to detect 3-word phrases ----------------
    nlp_models.train_bigram_model(
        input_path=path_input_clean_txt,
        model_path=path_output_model_mod,
        phrase_min_length=phrase_min_length,
        phrase_threshold=threshold,
        stopwords_set=stopwords_set
    )
    nlp_models.file_bigramer(
        input_path=path_input_clean_txt,
        output_path=path_output_transformed_txt,
        model_path=path_output_model_mod,
        scoring=scoring,
        threshold=threshold,
    )


"""word2vec model function"""


@seminlpclassify.qihangfuncs.timer_wrapper
def train_w2v_model(path_input_cleaned_txt, path_output_model, *args, **kwargs):
    """ Train a word2vec model using the LineSentence file in input_path,
    save the model to model_path.count

    Arguments:
        input_path {str} -- Corpus for training, each line is a sentence
        model_path {str} -- Where to save the model?
    """
    # pathlib.Path(path_output_model).parent.mkdir(parents=True, exist_ok=True)
    corpus_confcall = gensim.models.word2vec.PathLineSentences(
        str(path_input_cleaned_txt), max_sentence_length=10000000
    )
    model = gensim.models.Word2Vec(corpus_confcall, *args, **kwargs)
    model.save(str(path_output_model))


"""word dictionary semi-supervised under word2vec model, auto function"""


def auto_w2v_semisup_dict(
        path_input_w2v_model,
        seed_words_dict,
        restrict_vocab_per: typing.Optional[float],
        model_dims: int,

):
    model = gensim.models.Word2Vec.load(path_input_w2v_model)

    vocab_number = len(model.wv.vocab)

    print("Vocab size in the w2v model: {}".format(vocab_number))

    # expand dictionary
    expanded_words_dict = _dictionary.expand_words_dimension_mean(
        word2vec_model=model,
        seed_words=seed_words_dict,
        restrict=restrict_vocab_per,
        n=model_dims,
    )

    # make sure that one word only loads to one dimension
    expanded_words_dict = _dictionary.deduplicate_keywords(
        word2vec_model=model,
        expanded_words=expanded_words_dict,
        seed_words=seed_words_dict,
    )

    # rank the words under each dimension by similarity to the seed words
    expanded_words_dict = _dictionary.rank_by_sim(
        expanded_words_dict, seed_words_dict, model
    )
    # output the dictionary
    return expanded_words_dict
