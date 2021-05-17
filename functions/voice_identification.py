import os
import shutil
import pickle
import webrtcvad
from sklearn.mixture import GaussianMixture
from .model import map_adaptation
from .data_preprocess import *
import copy
import joblib

SR = 8000  # sample rate
N_MFCC = 13  # number of MFCC to extract
N_FFT = 0.020  # length of the FFT window in seconds
HOP_LENGTH = 0.010  # number of samples between successive frames in seconds
N_COMPONENTS = 16  # number of gaussians
COVARINACE_TYPE = 'diag'  # cov type for GMM


def get_data(file, result_file):
    y, sr = librosa.load(file, sr=SR)
    pre_emphasis = 0.97
    y = np.append(y[0], y[1:] - pre_emphasis * y[:-1])

    vad = webrtcvad.Vad(3)
    audio = np.int16(y / np.max(np.abs(y)) * 32768)

    frames = frame_generator(10, audio, sr)
    frames = list(frames)
    segments = vad_collector(sr, 50, 200, vad, frames)

    full_chunk = []
    for i, segment in enumerate(segments):
        full_chunk.append(segment[0: len(segment) - int(100 * sr / 1000)])
    write_wave(result_file, b''.join([full_chunk[i] for i in range(len(full_chunk))]), sr)
    return result_file


def get_features(file, features_to_file, features_from_file=None, mfcc=None):
    if features_from_file is not None:
        ubm_features = pickle.load(open(features_from_file, 'rb'))
    else:
        y, sr = librosa.load(file, sr=None)
        f = extract_features(np.array(y), sr, n_mfcc=N_MFCC if mfcc is None else mfcc, hop=HOP_LENGTH, window=N_FFT)
        ubm_features = normalize(f)
        pickle.dump(ubm_features, open(features_to_file, "wb"))
    return ubm_features


def get_ubm(ubm_features, ubm_file=None, ubm_to_file=None):
    if ubm_file is not None:
        ubm = joblib.load(ubm_file)
    else:
        ubm = GaussianMixture(n_components=N_COMPONENTS, covariance_type=COVARINACE_TYPE)
        ubm.fit(ubm_features)
        joblib.dump(ubm, ubm_to_file)
    return ubm


def get_gmm(ubm, gmm_features, gmm_to_file, gmm_file=None):
    if gmm_file is not None:
        gmm = joblib.load(gmm_file)
    else:
        gmm = copy.deepcopy(ubm)
        gmm = map_adaptation(gmm, gmm_features, max_iterations=1, relevance_factor=16)
        joblib.dump(gmm, gmm_to_file)
    return gmm


def clear_dir(path):
    shutil.rmtree(path)
    os.mkdir(path, mode=0o777, dir_fd=None)


def make_features(path, mfcc):
    data = get_data(file=path + '/1.wav',
                    result_file=path + '/speaker.wav')
    feature = get_features(file=data,
                           features_to_file=path + '/features.pkl', mfcc=mfcc)
    return feature


def create_gmm(app, path_ubm, id_):
    ubm_name = path_ubm
    path = app['config']['inventory']['dir'] + '/{0}/'.format(id_) + app['config']['inventory']['voiceDirName']
    gmm_features = np.asarray(make_features(path, N_COMPONENTS))
    ubm = get_ubm(None, ubm_file=ubm_name)
    gmm = get_gmm(ubm, gmm_features,
                  gmm_to_file=app['config']['inventory']['dir'] + '/{0}/'.format(id_) +
                              app['config']['inventory']['voiceDirName'] + '/1.pkl')


def form_models_list(app):
    answer = []
    for user in os.listdir(app['config']['inventory']['dir']):
        model_path = app['config']['inventory']['dir'] + '/{0}/'.format(user) + \
                     app['config']['inventory']['voiceDirName'] + '/1.pkl'
        if os.path.exists(model_path):
            answer.append(model_path)
    return answer


def predict_voice(app, file, features_path):
    models = form_models_list(app)
    answer_speaker = 0
    answer_score = -1e9
    gmm_features = np.asarray(get_features(file=file,
                                           features_to_file=features_path + '/check.pkl',
                                           mfcc=N_COMPONENTS))
    for model_path in models:
        model = get_gmm(None, None, None, gmm_file=model_path)
        s = np.array(model.score(gmm_features))
        if answer_score < s:
            answer_score = s
            answer_speaker = model_path
    answer_speaker = answer_speaker[len(app['config']['inventory']['dir']) + 1:
                                    len(app['config']['inventory']['voiceDirName'] + '//1.pkl')]
    if answer_score < -app['config']['voiceSystem']['border']:
        answer_speaker = -1
    return answer_speaker  # id_
