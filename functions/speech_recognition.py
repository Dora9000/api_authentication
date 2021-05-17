import numpy as np
from .data_generator import AudioGenerator
from keras import backend as K
from .utils import int_sequence_to_text
from IPython.display import Audio
from .sample_models import *


def get_predictions(audio_path, input_to_softmax, model_path):
    data_gen = AudioGenerator(spectrogram=False)
    data_gen.load_train_data()
    data_gen.load_validation_data()
    data_point = data_gen.normalize(data_gen.featurize(audio_path))

    input_to_softmax.load_weights(model_path)
    prediction = input_to_softmax.predict(np.expand_dims(data_point, axis=0))
    output_length = [input_to_softmax.output_length(data_point.shape[0])]
    pred_ints = (K.eval(K.ctc_decode(
        prediction, output_length)[0][0]) + 1).flatten().tolist()

    return ''.join(int_sequence_to_text(pred_ints))


model_end = final_model(input_dim=13,
                        filters=200,
                        kernel_size=11,
                        conv_stride=2,
                        conv_border_mode='valid',
                        units=250,
                        activation='relu',
                        cell=GRU,
                        dropout_rate=1,
                        number_of_layers=2)


def predict(app, file):
    model_path = app['config']['languageSystem']['dir'] + '/model_5.h5'
    answer = get_predictions(audio_path=file,
                             input_to_softmax=model_end,
                             model_path=model_path)
    return answer