from flask import Flask, request, jsonify
import io
import json
from io import BytesIO
import tensorflow as tf
from matplotlib import pyplot as plt
from tensorflow import keras

from keras import layers
from keras.models import load_model
from PIL import Image, ImageChops, ImageOps
import base64
import numpy as np
from flask_cors import CORS

print(tf.__version__)
app = Flask(__name__)
CORS(app)

max_length = 58
uniqueLabels = ['barline', 'clef-C1', 'clef-C2', 'clef-C3', 'clef-C4', 'clef-C5', 'clef-F3', 'clef-F4', 'clef-F5',
                'clef-G1', 'clef-G2', 'gracenote-A#3_eighth', 'gracenote-A#3_sixteenth', 'gracenote-A#4_eighth',
                'gracenote-A#4_half', 'gracenote-A#4_quarter', 'gracenote-A#4_sixteenth', 'gracenote-A#4_thirty_second',
                'gracenote-A2_eighth', 'gracenote-A2_quarter', 'gracenote-A2_sixteenth', 'gracenote-A3_eighth',
                'gracenote-A3_half', 'gracenote-A3_quarter', 'gracenote-A3_sixteenth', 'gracenote-A3_thirty_second',
                'gracenote-A4_eighth', 'gracenote-A4_half', 'gracenote-A4_quarter', 'gracenote-A4_sixteenth',
                'gracenote-A4_thirty_second', 'gracenote-A5_eighth', 'gracenote-A5_quarter', 'gracenote-A5_sixteenth',
                'gracenote-A5_thirty_second', 'gracenote-Ab3_eighth', 'gracenote-Ab3_sixteenth',
                'gracenote-Ab3_thirty_second', 'gracenote-Ab4_eighth', 'gracenote-Ab4_half', 'gracenote-Ab4_quarter',
                'gracenote-Ab4_sixteenth', 'gracenote-Ab4_thirty_second', 'gracenote-Ab5_eighth',
                'gracenote-Ab5_quarter', 'gracenote-Ab5_sixteenth', 'gracenote-Ab5_thirty_second',
                'gracenote-B#4_quarter', 'gracenote-B#4_sixteenth', 'gracenote-B3_eighth', 'gracenote-B3_quarter',
                'gracenote-B3_sixteenth', 'gracenote-B3_thirty_second', 'gracenote-B4_eighth', 'gracenote-B4_quarter',
                'gracenote-B4_sixteenth', 'gracenote-B4_thirty_second', 'gracenote-Bb3_eighth', 'gracenote-Bb3_quarter',
                'gracenote-Bb3_sixteenth', 'gracenote-Bb3_thirty_second', 'gracenote-Bb4_eighth', 'gracenote-Bb4_half',
                'gracenote-Bb4_quarter', 'gracenote-Bb4_sixteenth', 'gracenote-Bb4_thirty_second',
                'gracenote-C#3_eighth', 'gracenote-C#4_eighth', 'gracenote-C#4_quarter', 'gracenote-C#4_sixteenth',
                'gracenote-C#4_thirty_second', 'gracenote-C#5_eighth', 'gracenote-C#5_eighth.', 'gracenote-C#5_half',
                'gracenote-C#5_quarter', 'gracenote-C#5_sixteenth', 'gracenote-C#5_sixteenth.',
                'gracenote-C#5_thirty_second', 'gracenote-C3_eighth', 'gracenote-C3_quarter', 'gracenote-C3_sixteenth',
                'gracenote-C4_eighth', 'gracenote-C4_quarter', 'gracenote-C4_sixteenth', 'gracenote-C4_thirty_second',
                'gracenote-C5_eighth', 'gracenote-C5_half', 'gracenote-C5_quarter', 'gracenote-C5_sixteenth',
                'gracenote-C5_thirty_second', 'gracenote-Cb5_eighth', 'gracenote-Cb5_quarter',
                'gracenote-Cb5_thirty_second', 'gracenote-D#3_quarter', 'gracenote-D#3_sixteenth',
                'gracenote-D#4_eighth', 'gracenote-D#4_quarter', 'gracenote-D#4_sixteenth',
                'gracenote-D#4_thirty_second', 'gracenote-D#5_eighth', 'gracenote-D#5_quarter',
                'gracenote-D#5_sixteenth', 'gracenote-D#5_thirty_second', 'gracenote-D3_eighth',
                'gracenote-D3_sixteenth', 'gracenote-D4_eighth', 'gracenote-D4_quarter', 'gracenote-D4_sixteenth',
                'gracenote-D4_thirty_second', 'gracenote-D5_eighth', 'gracenote-D5_half', 'gracenote-D5_quarter',
                'gracenote-D5_sixteenth', 'gracenote-D5_thirty_second', 'gracenote-Db4_eighth',
                'gracenote-Db4_sixteenth', 'gracenote-Db5_eighth', 'gracenote-Db5_half', 'gracenote-Db5_quarter',
                'gracenote-Db5_sixteenth', 'gracenote-Db5_thirty_second', 'gracenote-E#5_eighth',
                'gracenote-E#5_quarter', 'gracenote-E#5_sixteenth', 'gracenote-E3_eighth', 'gracenote-E3_quarter',
                'gracenote-E4_eighth', 'gracenote-E4_quarter', 'gracenote-E4_sixteenth', 'gracenote-E4_thirty_second',
                'gracenote-E5_eighth', 'gracenote-E5_half', 'gracenote-E5_quarter', 'gracenote-E5_sixteenth',
                'gracenote-E5_thirty_second', 'gracenote-Eb3_eighth', 'gracenote-Eb3_quarter',
                'gracenote-Eb3_sixteenth', 'gracenote-Eb4_eighth', 'gracenote-Eb4_quarter', 'gracenote-Eb4_sixteenth',
                'gracenote-Eb4_thirty_second', 'gracenote-Eb5_eighth', 'gracenote-Eb5_quarter',
                'gracenote-Eb5_sixteenth', 'gracenote-Eb5_thirty_second', 'gracenote-F#3_eighth',
                'gracenote-F#3_quarter', 'gracenote-F#3_sixteenth', 'gracenote-F#4_eighth', 'gracenote-F#4_quarter',
                'gracenote-F#4_sixteenth', 'gracenote-F#4_thirty_second', 'gracenote-F#5_eighth',
                'gracenote-F#5_quarter', 'gracenote-F#5_sixteenth', 'gracenote-F#5_thirty_second',
                'gracenote-F2_eighth', 'gracenote-F3_eighth', 'gracenote-F3_quarter', 'gracenote-F3_sixteenth',
                'gracenote-F4_eighth', 'gracenote-F4_quarter', 'gracenote-F4_sixteenth', 'gracenote-F4_thirty_second',
                'gracenote-F5_eighth', 'gracenote-F5_half', 'gracenote-F5_quarter', 'gracenote-F5_sixteenth',
                'gracenote-F5_thirty_second', 'gracenote-G#3_sixteenth', 'gracenote-G#3_thirty_second',
                'gracenote-G#4_eighth', 'gracenote-G#4_quarter', 'gracenote-G#4_sixteenth',
                'gracenote-G#4_thirty_second', 'gracenote-G#5_eighth', 'gracenote-G#5_quarter',
                'gracenote-G#5_sixteenth', 'gracenote-G#5_thirty_second', 'gracenote-G3_eighth', 'gracenote-G3_quarter',
                'gracenote-G3_sixteenth', 'gracenote-G3_thirty_second', 'gracenote-G4_eighth', 'gracenote-G4_eighth.',
                'gracenote-G4_quarter', 'gracenote-G4_sixteenth', 'gracenote-G4_thirty_second', 'gracenote-G5_eighth',
                'gracenote-G5_half', 'gracenote-G5_quarter', 'gracenote-G5_sixteenth', 'gracenote-G5_thirty_second',
                'gracenote-Gb4_eighth', 'gracenote-Gb4_quarter', 'gracenote-Gb5_thirty_second', 'keySignature-AM',
                'keySignature-AbM', 'keySignature-BM', 'keySignature-BbM', 'keySignature-C#M', 'keySignature-DM',
                'keySignature-DbM', 'keySignature-EM', 'keySignature-EbM', 'keySignature-F#M', 'keySignature-FM',
                'keySignature-GM', 'keySignature-GbM', 'multirest-1', 'multirest-10', 'multirest-100', 'multirest-11',
                'multirest-112', 'multirest-12', 'multirest-13', 'multirest-14', 'multirest-15', 'multirest-16',
                'multirest-164', 'multirest-17', 'multirest-18', 'multirest-19', 'multirest-2', 'multirest-20',
                'multirest-21', 'multirest-22', 'multirest-225', 'multirest-23', 'multirest-24', 'multirest-25',
                'multirest-26', 'multirest-27', 'multirest-28', 'multirest-29', 'multirest-3', 'multirest-30',
                'multirest-31', 'multirest-32', 'multirest-33', 'multirest-34', 'multirest-35', 'multirest-36',
                'multirest-37', 'multirest-38', 'multirest-39', 'multirest-4', 'multirest-40', 'multirest-41',
                'multirest-42', 'multirest-43', 'multirest-44', 'multirest-45', 'multirest-46', 'multirest-47',
                'multirest-48', 'multirest-49', 'multirest-5', 'multirest-51', 'multirest-52', 'multirest-53',
                'multirest-54', 'multirest-55', 'multirest-56', 'multirest-57', 'multirest-58', 'multirest-59',
                'multirest-6', 'multirest-60', 'multirest-63', 'multirest-64', 'multirest-66', 'multirest-67',
                'multirest-69', 'multirest-7', 'multirest-71', 'multirest-73', 'multirest-77', 'multirest-8',
                'multirest-80', 'multirest-9', 'multirest-98', 'note-A#2_eighth', 'note-A#2_quarter',
                'note-A#2_sixteenth', 'note-A#2_sixteenth.', 'note-A#3_eighth', 'note-A#3_eighth.', 'note-A#3_half',
                'note-A#3_half.', 'note-A#3_half_fermata', 'note-A#3_quarter', 'note-A#3_quarter.',
                'note-A#3_sixteenth', 'note-A#3_sixty_fourth', 'note-A#3_thirty_second', 'note-A#3_whole',
                'note-A#4_eighth', 'note-A#4_eighth.', 'note-A#4_half', 'note-A#4_half_fermata', 'note-A#4_quarter',
                'note-A#4_quarter.', 'note-A#4_quarter_fermata', 'note-A#4_sixteenth', 'note-A#4_sixteenth.',
                'note-A#4_thirty_second', 'note-A#4_whole', 'note-A#5_eighth', 'note-A#5_half', 'note-A#5_half.',
                'note-A#5_quarter', 'note-A#5_quarter.', 'note-A#5_sixteenth', 'note-A#5_sixteenth.',
                'note-A#5_thirty_second', 'note-A2_double_whole', 'note-A2_double_whole.', 'note-A2_eighth',
                'note-A2_eighth.', 'note-A2_half', 'note-A2_half.', 'note-A2_half_fermata', 'note-A2_quadruple_whole',
                'note-A2_quadruple_whole_fermata', 'note-A2_quarter', 'note-A2_quarter.', 'note-A2_quarter_fermata',
                'note-A2_sixteenth', 'note-A2_thirty_second', 'note-A2_whole', 'note-A2_whole.', 'note-A3_double_whole',
                'note-A3_double_whole.', 'note-A3_double_whole_fermata', 'note-A3_eighth', 'note-A3_eighth.',
                'note-A3_eighth._fermata', 'note-A3_eighth_fermata', 'note-A3_half', 'note-A3_half.',
                'note-A3_half._fermata', 'note-A3_half_fermata', 'note-A3_quarter', 'note-A3_quarter.',
                'note-A3_quarter..', 'note-A3_quarter_fermata', 'note-A3_sixteenth', 'note-A3_sixteenth.',
                'note-A3_sixty_fourth', 'note-A3_thirty_second', 'note-A3_whole', 'note-A3_whole.',
                'note-A3_whole_fermata', 'note-A4_double_whole', 'note-A4_double_whole.',
                'note-A4_double_whole_fermata', 'note-A4_eighth', 'note-A4_eighth.', 'note-A4_eighth..',
                'note-A4_eighth_fermata', 'note-A4_half', 'note-A4_half.', 'note-A4_half..', 'note-A4_half._fermata',
                'note-A4_half_fermata', 'note-A4_quadruple_whole', 'note-A4_quadruple_whole.', 'note-A4_quarter',
                'note-A4_quarter.', 'note-A4_quarter..', 'note-A4_quarter._fermata', 'note-A4_quarter_fermata',
                'note-A4_sixteenth', 'note-A4_sixteenth.', 'note-A4_sixty_fourth', 'note-A4_thirty_second',
                'note-A4_whole', 'note-A4_whole.', 'note-A4_whole._fermata', 'note-A4_whole_fermata',
                'note-A5_double_whole', 'note-A5_eighth', 'note-A5_eighth.', 'note-A5_eighth..', 'note-A5_half',
                'note-A5_half.', 'note-A5_half._fermata', 'note-A5_half_fermata', 'note-A5_quarter', 'note-A5_quarter.',
                'note-A5_quarter..', 'note-A5_quarter._fermata', 'note-A5_quarter_fermata', 'note-A5_sixteenth',
                'note-A5_sixteenth.', 'note-A5_sixty_fourth', 'note-A5_thirty_second', 'note-A5_thirty_second.',
                'note-A5_whole', 'note-A5_whole.', 'note-A5_whole_fermata', 'note-Ab2_eighth', 'note-Ab2_eighth.',
                'note-Ab2_half', 'note-Ab2_half.', 'note-Ab2_half_fermata', 'note-Ab2_quarter', 'note-Ab2_quarter.',
                'note-Ab2_sixteenth', 'note-Ab3_eighth', 'note-Ab3_eighth.', 'note-Ab3_half', 'note-Ab3_half.',
                'note-Ab3_quarter', 'note-Ab3_quarter.', 'note-Ab3_quarter..', 'note-Ab3_sixteenth',
                'note-Ab3_sixteenth.', 'note-Ab3_thirty_second', 'note-Ab3_whole', 'note-Ab4_eighth',
                'note-Ab4_eighth.', 'note-Ab4_eighth..', 'note-Ab4_half', 'note-Ab4_half.', 'note-Ab4_half._fermata',
                'note-Ab4_half_fermata', 'note-Ab4_quarter', 'note-Ab4_quarter.', 'note-Ab4_quarter..',
                'note-Ab4_quarter_fermata', 'note-Ab4_sixteenth', 'note-Ab4_sixteenth.', 'note-Ab4_sixty_fourth',
                'note-Ab4_thirty_second', 'note-Ab4_whole', 'note-Ab4_whole.', 'note-Ab5_eighth', 'note-Ab5_eighth.',
                'note-Ab5_eighth..', 'note-Ab5_half', 'note-Ab5_half.', 'note-Ab5_half._fermata', 'note-Ab5_quarter',
                'note-Ab5_quarter.', 'note-Ab5_sixteenth', 'note-Ab5_sixteenth.', 'note-Ab5_sixty_fourth',
                'note-Ab5_thirty_second', 'note-Ab5_whole', 'note-B#2_eighth', 'note-B#2_eighth.', 'note-B#2_half',
                'note-B#2_quarter', 'note-B#2_sixteenth', 'note-B#3_double_whole', 'note-B#3_double_whole.',
                'note-B#3_eighth', 'note-B#3_eighth.', 'note-B#3_half', 'note-B#3_quarter', 'note-B#3_sixteenth',
                'note-B#3_whole', 'note-B#4_double_whole', 'note-B#4_double_whole_fermata', 'note-B#4_eighth',
                'note-B#4_eighth.', 'note-B#4_half', 'note-B#4_half.', 'note-B#4_quarter', 'note-B#4_quarter.',
                'note-B#4_sixteenth', 'note-B#4_sixteenth.', 'note-B#4_whole', 'note-B#4_whole.', 'note-B#5_eighth',
                'note-B#5_quarter', 'note-B#5_sixteenth', 'note-B1_quarter', 'note-B2_double_whole', 'note-B2_eighth',
                'note-B2_eighth.', 'note-B2_half', 'note-B2_half.', 'note-B2_half_fermata', 'note-B2_quarter',
                'note-B2_quarter.', 'note-B2_sixteenth', 'note-B2_thirty_second', 'note-B2_whole', 'note-B2_whole.',
                'note-B3_double_whole', 'note-B3_double_whole.', 'note-B3_double_whole_fermata', 'note-B3_eighth',
                'note-B3_eighth.', 'note-B3_half', 'note-B3_half.', 'note-B3_half_fermata', 'note-B3_quarter',
                'note-B3_quarter.', 'note-B3_quarter..', 'note-B3_quarter_fermata', 'note-B3_sixteenth',
                'note-B3_sixteenth.', 'note-B3_sixty_fourth', 'note-B3_thirty_second', 'note-B3_whole',
                'note-B3_whole.', 'note-B3_whole_fermata', 'note-B4_double_whole', 'note-B4_double_whole.',
                'note-B4_eighth', 'note-B4_eighth.', 'note-B4_eighth..', 'note-B4_eighth_fermata', 'note-B4_half',
                'note-B4_half.', 'note-B4_half._fermata', 'note-B4_half_fermata', 'note-B4_quadruple_whole',
                'note-B4_quarter', 'note-B4_quarter.', 'note-B4_quarter..', 'note-B4_quarter._fermata',
                'note-B4_quarter_fermata', 'note-B4_sixteenth', 'note-B4_sixteenth.', 'note-B4_sixteenth._fermata',
                'note-B4_sixty_fourth', 'note-B4_thirty_second', 'note-B4_thirty_second.', 'note-B4_whole',
                'note-B4_whole.', 'note-B4_whole._fermata', 'note-B4_whole_fermata', 'note-B5_eighth',
                'note-B5_eighth.', 'note-B5_eighth..', 'note-B5_half', 'note-B5_half.', 'note-B5_quarter',
                'note-B5_quarter.', 'note-B5_quarter..', 'note-B5_sixteenth', 'note-B5_sixteenth.',
                'note-B5_sixty_fourth', 'note-B5_thirty_second', 'note-B5_whole', 'note-Bb2_double_whole',
                'note-Bb2_eighth', 'note-Bb2_eighth.', 'note-Bb2_half', 'note-Bb2_half.', 'note-Bb2_quarter',
                'note-Bb2_quarter.', 'note-Bb2_quarter._fermata', 'note-Bb2_sixteenth', 'note-Bb2_sixteenth.',
                'note-Bb2_thirty_second', 'note-Bb2_whole', 'note-Bb2_whole.', 'note-Bb3_double_whole',
                'note-Bb3_double_whole.', 'note-Bb3_eighth', 'note-Bb3_eighth.', 'note-Bb3_eighth..', 'note-Bb3_half',
                'note-Bb3_half.', 'note-Bb3_half._fermata', 'note-Bb3_half_fermata', 'note-Bb3_quarter',
                'note-Bb3_quarter.', 'note-Bb3_quarter..', 'note-Bb3_quarter._fermata', 'note-Bb3_quarter_fermata',
                'note-Bb3_sixteenth', 'note-Bb3_sixteenth.', 'note-Bb3_sixty_fourth', 'note-Bb3_thirty_second',
                'note-Bb3_whole', 'note-Bb3_whole.', 'note-Bb4_double_whole', 'note-Bb4_double_whole.',
                'note-Bb4_eighth', 'note-Bb4_eighth.', 'note-Bb4_eighth..', 'note-Bb4_half', 'note-Bb4_half.',
                'note-Bb4_half._fermata', 'note-Bb4_half_fermata', 'note-Bb4_quadruple_whole', 'note-Bb4_quarter',
                'note-Bb4_quarter.', 'note-Bb4_quarter..', 'note-Bb4_quarter._fermata', 'note-Bb4_quarter_fermata',
                'note-Bb4_sixteenth', 'note-Bb4_sixteenth.', 'note-Bb4_sixty_fourth', 'note-Bb4_thirty_second',
                'note-Bb4_whole', 'note-Bb4_whole.', 'note-Bb4_whole._fermata', 'note-Bb4_whole_fermata',
                'note-Bb5_eighth', 'note-Bb5_eighth.', 'note-Bb5_eighth..', 'note-Bb5_half', 'note-Bb5_half.',
                'note-Bb5_half_fermata', 'note-Bb5_quarter', 'note-Bb5_quarter.', 'note-Bb5_quarter..',
                'note-Bb5_sixteenth', 'note-Bb5_sixteenth.', 'note-Bb5_sixty_fourth', 'note-Bb5_thirty_second',
                'note-Bb5_thirty_second.', 'note-Bb5_whole', 'note-Bb5_whole_fermata', 'note-C#2_eighth',
                'note-C#2_eighth.', 'note-C#2_quarter', 'note-C#3_eighth', 'note-C#3_eighth.', 'note-C#3_half',
                'note-C#3_half.', 'note-C#3_quarter', 'note-C#3_quarter.', 'note-C#3_sixteenth', 'note-C#3_sixteenth.',
                'note-C#3_thirty_second', 'note-C#3_whole', 'note-C#4_eighth', 'note-C#4_eighth.',
                'note-C#4_eighth_fermata', 'note-C#4_half', 'note-C#4_half.', 'note-C#4_half_fermata',
                'note-C#4_quadruple_whole_fermata', 'note-C#4_quarter', 'note-C#4_quarter.', 'note-C#4_quarter..',
                'note-C#4_quarter._fermata', 'note-C#4_quarter_fermata', 'note-C#4_sixteenth', 'note-C#4_sixteenth.',
                'note-C#4_sixty_fourth', 'note-C#4_thirty_second', 'note-C#4_whole', 'note-C#4_whole.',
                'note-C#5_double_whole', 'note-C#5_eighth', 'note-C#5_eighth.', 'note-C#5_eighth..',
                'note-C#5_eighth._fermata', 'note-C#5_eighth_fermata', 'note-C#5_half', 'note-C#5_half.',
                'note-C#5_half._fermata', 'note-C#5_half_fermata', 'note-C#5_quarter', 'note-C#5_quarter.',
                'note-C#5_quarter..', 'note-C#5_quarter_fermata', 'note-C#5_sixteenth', 'note-C#5_sixteenth.',
                'note-C#5_sixty_fourth', 'note-C#5_thirty_second', 'note-C#5_whole', 'note-C#5_whole.',
                'note-C#5_whole_fermata', 'note-C#6_eighth', 'note-C#6_eighth.', 'note-C#6_half', 'note-C#6_half.',
                'note-C#6_half_fermata', 'note-C#6_quarter', 'note-C#6_quarter.', 'note-C#6_quarter..',
                'note-C#6_sixteenth', 'note-C#6_sixteenth.', 'note-C#6_sixty_fourth', 'note-C#6_thirty_second',
                'note-C#6_whole_fermata', 'note-C2_double_whole.', 'note-C2_eighth', 'note-C2_half', 'note-C2_quarter',
                'note-C2_quarter.', 'note-C2_sixteenth', 'note-C2_whole', 'note-C3_double_whole',
                'note-C3_double_whole.', 'note-C3_eighth', 'note-C3_eighth.', 'note-C3_half', 'note-C3_half.',
                'note-C3_half_fermata', 'note-C3_quadruple_whole', 'note-C3_quadruple_whole.', 'note-C3_quarter',
                'note-C3_quarter.', 'note-C3_sixteenth', 'note-C3_sixteenth.', 'note-C3_thirty_second', 'note-C3_whole',
                'note-C3_whole.', 'note-C3_whole_fermata', 'note-C4_double_whole', 'note-C4_double_whole.',
                'note-C4_double_whole_fermata', 'note-C4_eighth', 'note-C4_eighth.', 'note-C4_eighth..',
                'note-C4_eighth_fermata', 'note-C4_half', 'note-C4_half.', 'note-C4_half_fermata',
                'note-C4_quadruple_whole', 'note-C4_quadruple_whole.', 'note-C4_quarter', 'note-C4_quarter.',
                'note-C4_quarter..', 'note-C4_quarter_fermata', 'note-C4_sixteenth', 'note-C4_sixteenth.',
                'note-C4_sixty_fourth', 'note-C4_thirty_second', 'note-C4_whole', 'note-C4_whole.',
                'note-C4_whole_fermata', 'note-C5_double_whole', 'note-C5_double_whole.',
                'note-C5_double_whole._fermata', 'note-C5_double_whole_fermata', 'note-C5_eighth', 'note-C5_eighth.',
                'note-C5_eighth..', 'note-C5_eighth._fermata', 'note-C5_eighth_fermata', 'note-C5_half',
                'note-C5_half.', 'note-C5_half._fermata', 'note-C5_half_fermata', 'note-C5_quadruple_whole',
                'note-C5_quadruple_whole.', 'note-C5_quadruple_whole_fermata', 'note-C5_quarter', 'note-C5_quarter.',
                'note-C5_quarter..', 'note-C5_quarter._fermata', 'note-C5_quarter_fermata', 'note-C5_sixteenth',
                'note-C5_sixteenth.', 'note-C5_sixty_fourth', 'note-C5_thirty_second', 'note-C5_thirty_second.',
                'note-C5_whole', 'note-C5_whole.', 'note-C5_whole._fermata', 'note-C5_whole_fermata', 'note-C6_eighth',
                'note-C6_eighth.', 'note-C6_eighth..', 'note-C6_half', 'note-C6_half.', 'note-C6_half..',
                'note-C6_half._fermata', 'note-C6_half_fermata', 'note-C6_quarter', 'note-C6_quarter.',
                'note-C6_quarter..', 'note-C6_sixteenth', 'note-C6_sixteenth.', 'note-C6_sixty_fourth',
                'note-C6_thirty_second', 'note-C6_whole', 'note-C6_whole_fermata', 'note-Cb3_quarter',
                'note-Cb4_eighth', 'note-Cb4_eighth.', 'note-Cb4_quarter', 'note-Cb4_quarter.', 'note-Cb5_eighth',
                'note-Cb5_eighth.', 'note-Cb5_half', 'note-Cb5_half.', 'note-Cb5_quarter', 'note-Cb5_quarter.',
                'note-Cb5_sixteenth', 'note-Cb5_thirty_second', 'note-Cb5_whole', 'note-Cb6_eighth', 'note-Cb6_quarter',
                'note-Cb6_sixteenth', 'note-D#2_quarter', 'note-D#2_sixteenth', 'note-D#3_eighth', 'note-D#3_eighth.',
                'note-D#3_half', 'note-D#3_half_fermata', 'note-D#3_quarter', 'note-D#3_quarter.', 'note-D#3_sixteenth',
                'note-D#3_thirty_second', 'note-D#3_whole', 'note-D#4_eighth', 'note-D#4_eighth.', 'note-D#4_half',
                'note-D#4_half.', 'note-D#4_quarter', 'note-D#4_quarter.', 'note-D#4_sixteenth', 'note-D#4_sixteenth.',
                'note-D#4_thirty_second', 'note-D#4_whole', 'note-D#5_double_whole', 'note-D#5_eighth',
                'note-D#5_eighth.', 'note-D#5_eighth..', 'note-D#5_eighth_fermata', 'note-D#5_half', 'note-D#5_half.',
                'note-D#5_half_fermata', 'note-D#5_quarter', 'note-D#5_quarter.', 'note-D#5_quarter_fermata',
                'note-D#5_sixteenth', 'note-D#5_sixteenth.', 'note-D#5_sixty_fourth', 'note-D#5_thirty_second',
                'note-D#5_whole', 'note-D#5_whole_fermata', 'note-D#6_eighth', 'note-D#6_eighth..', 'note-D#6_half',
                'note-D#6_quarter', 'note-D#6_sixteenth', 'note-D#6_thirty_second', 'note-D2_double_whole',
                'note-D2_eighth', 'note-D2_eighth.', 'note-D2_half', 'note-D2_quarter', 'note-D2_quarter._fermata',
                'note-D2_thirty_second', 'note-D2_whole', 'note-D3_double_whole', 'note-D3_double_whole.',
                'note-D3_eighth', 'note-D3_eighth.', 'note-D3_half', 'note-D3_half.', 'note-D3_half_fermata',
                'note-D3_quadruple_whole', 'note-D3_quadruple_whole_fermata', 'note-D3_quarter', 'note-D3_quarter.',
                'note-D3_quarter..', 'note-D3_quarter_fermata', 'note-D3_sixteenth', 'note-D3_sixteenth.',
                'note-D3_thirty_second', 'note-D3_whole', 'note-D3_whole.', 'note-D3_whole_fermata',
                'note-D4_double_whole', 'note-D4_double_whole.', 'note-D4_double_whole_fermata', 'note-D4_eighth',
                'note-D4_eighth.', 'note-D4_eighth..', 'note-D4_eighth_fermata', 'note-D4_half', 'note-D4_half.',
                'note-D4_half._fermata', 'note-D4_half_fermata', 'note-D4_quadruple_whole', 'note-D4_quarter',
                'note-D4_quarter.', 'note-D4_quarter..', 'note-D4_quarter.._fermata', 'note-D4_quarter_fermata',
                'note-D4_sixteenth', 'note-D4_sixteenth.', 'note-D4_sixty_fourth', 'note-D4_thirty_second',
                'note-D4_whole', 'note-D4_whole.', 'note-D4_whole_fermata', 'note-D5_double_whole',
                'note-D5_double_whole.', 'note-D5_double_whole_fermata', 'note-D5_eighth', 'note-D5_eighth.',
                'note-D5_eighth..', 'note-D5_eighth._fermata', 'note-D5_eighth_fermata', 'note-D5_half',
                'note-D5_half.', 'note-D5_half._fermata', 'note-D5_half_fermata', 'note-D5_quadruple_whole',
                'note-D5_quadruple_whole_fermata', 'note-D5_quarter', 'note-D5_quarter.', 'note-D5_quarter..',
                'note-D5_quarter._fermata', 'note-D5_quarter_fermata', 'note-D5_sixteenth', 'note-D5_sixteenth.',
                'note-D5_sixty_fourth', 'note-D5_thirty_second', 'note-D5_thirty_second.', 'note-D5_whole',
                'note-D5_whole.', 'note-D5_whole._fermata', 'note-D5_whole_fermata', 'note-D6_eighth',
                'note-D6_eighth.', 'note-D6_eighth..', 'note-D6_half', 'note-D6_half.', 'note-D6_half..',
                'note-D6_half_fermata', 'note-D6_quarter', 'note-D6_quarter.', 'note-D6_quarter..',
                'note-D6_quarter._fermata', 'note-D6_quarter_fermata', 'note-D6_sixteenth', 'note-D6_sixteenth.',
                'note-D6_thirty_second', 'note-D6_whole', 'note-D6_whole.', 'note-D6_whole_fermata', 'note-Db3_eighth',
                'note-Db3_eighth.', 'note-Db3_half', 'note-Db3_half.', 'note-Db3_quarter', 'note-Db3_quarter.',
                'note-Db4_double_whole', 'note-Db4_eighth', 'note-Db4_eighth.', 'note-Db4_half', 'note-Db4_half.',
                'note-Db4_quarter', 'note-Db4_quarter.', 'note-Db4_sixteenth', 'note-Db4_sixteenth.',
                'note-Db4_thirty_second', 'note-Db4_whole', 'note-Db5_double_whole', 'note-Db5_eighth',
                'note-Db5_eighth.', 'note-Db5_eighth..', 'note-Db5_half', 'note-Db5_half.', 'note-Db5_half_fermata',
                'note-Db5_quarter', 'note-Db5_quarter.', 'note-Db5_quarter..', 'note-Db5_sixteenth',
                'note-Db5_sixteenth.', 'note-Db5_sixty_fourth', 'note-Db5_thirty_second', 'note-Db5_whole',
                'note-Db5_whole.', 'note-Db5_whole_fermata', 'note-Db6_eighth', 'note-Db6_eighth.', 'note-Db6_half',
                'note-Db6_quarter', 'note-Db6_quarter.', 'note-Db6_sixteenth', 'note-Db6_sixteenth.',
                'note-Db6_thirty_second', 'note-E#3_eighth', 'note-E#3_eighth.', 'note-E#3_half', 'note-E#3_quarter',
                'note-E#3_sixteenth', 'note-E#4_eighth', 'note-E#4_eighth..', 'note-E#4_half', 'note-E#4_quarter',
                'note-E#4_quarter.', 'note-E#4_sixteenth', 'note-E#4_sixty_fourth', 'note-E#4_whole', 'note-E#4_whole.',
                'note-E#5_eighth', 'note-E#5_eighth.', 'note-E#5_half', 'note-E#5_half.', 'note-E#5_half_fermata',
                'note-E#5_quarter', 'note-E#5_quarter.', 'note-E#5_sixteenth', 'note-E#5_sixteenth.',
                'note-E#5_thirty_second', 'note-E#6_sixteenth', 'note-E2_eighth', 'note-E2_eighth.', 'note-E2_half',
                'note-E2_half.', 'note-E2_quarter', 'note-E2_sixteenth', 'note-E2_whole', 'note-E2_whole_fermata',
                'note-E3_double_whole', 'note-E3_double_whole.', 'note-E3_double_whole_fermata', 'note-E3_eighth',
                'note-E3_eighth.', 'note-E3_half', 'note-E3_half.', 'note-E3_half._fermata', 'note-E3_half_fermata',
                'note-E3_quadruple_whole', 'note-E3_quarter', 'note-E3_quarter.', 'note-E3_quarter._fermata',
                'note-E3_quarter_fermata', 'note-E3_sixteenth', 'note-E3_sixteenth.', 'note-E3_thirty_second',
                'note-E3_whole', 'note-E3_whole.', 'note-E3_whole_fermata', 'note-E4_double_whole',
                'note-E4_double_whole.', 'note-E4_double_whole_fermata', 'note-E4_eighth', 'note-E4_eighth.',
                'note-E4_eighth..', 'note-E4_half', 'note-E4_half.', 'note-E4_half._fermata', 'note-E4_half_fermata',
                'note-E4_quadruple_whole', 'note-E4_quadruple_whole.', 'note-E4_quadruple_whole_fermata',
                'note-E4_quarter', 'note-E4_quarter.', 'note-E4_quarter..', 'note-E4_quarter._fermata',
                'note-E4_quarter_fermata', 'note-E4_sixteenth', 'note-E4_sixteenth.', 'note-E4_sixty_fourth',
                'note-E4_thirty_second', 'note-E4_whole', 'note-E4_whole.', 'note-E4_whole_fermata',
                'note-E5_double_whole', 'note-E5_double_whole.', 'note-E5_eighth', 'note-E5_eighth.',
                'note-E5_eighth..', 'note-E5_eighth_fermata', 'note-E5_half', 'note-E5_half.', 'note-E5_half..',
                'note-E5_half._fermata', 'note-E5_half_fermata', 'note-E5_quadruple_whole_fermata', 'note-E5_quarter',
                'note-E5_quarter.', 'note-E5_quarter..', 'note-E5_quarter._fermata', 'note-E5_quarter_fermata',
                'note-E5_sixteenth', 'note-E5_sixteenth.', 'note-E5_sixteenth_fermata', 'note-E5_sixty_fourth',
                'note-E5_thirty_second', 'note-E5_whole', 'note-E5_whole.', 'note-E5_whole._fermata',
                'note-E5_whole_fermata', 'note-E6_eighth', 'note-E6_eighth.', 'note-E6_eighth..', 'note-E6_half',
                'note-E6_half.', 'note-E6_quarter', 'note-E6_quarter.', 'note-E6_sixteenth', 'note-E6_sixteenth.',
                'note-E6_thirty_second', 'note-Eb2_eighth', 'note-Eb2_half', 'note-Eb2_quarter', 'note-Eb2_quarter.',
                'note-Eb2_sixteenth', 'note-Eb2_whole', 'note-Eb3_eighth', 'note-Eb3_eighth.', 'note-Eb3_half',
                'note-Eb3_half.', 'note-Eb3_half._fermata', 'note-Eb3_half_fermata', 'note-Eb3_quarter',
                'note-Eb3_quarter.', 'note-Eb3_quarter_fermata', 'note-Eb3_sixteenth', 'note-Eb3_sixteenth.',
                'note-Eb3_thirty_second', 'note-Eb3_whole', 'note-Eb3_whole.', 'note-Eb4_double_whole',
                'note-Eb4_eighth', 'note-Eb4_eighth.', 'note-Eb4_eighth..', 'note-Eb4_eighth._fermata', 'note-Eb4_half',
                'note-Eb4_half.', 'note-Eb4_half._fermata', 'note-Eb4_half_fermata', 'note-Eb4_quarter',
                'note-Eb4_quarter.', 'note-Eb4_quarter..', 'note-Eb4_quarter_fermata', 'note-Eb4_sixteenth',
                'note-Eb4_sixteenth.', 'note-Eb4_sixty_fourth', 'note-Eb4_thirty_second', 'note-Eb4_whole',
                'note-Eb4_whole.', 'note-Eb4_whole_fermata', 'note-Eb5_double_whole', 'note-Eb5_eighth',
                'note-Eb5_eighth.', 'note-Eb5_eighth..', 'note-Eb5_eighth_fermata', 'note-Eb5_half', 'note-Eb5_half.',
                'note-Eb5_half._fermata', 'note-Eb5_half_fermata', 'note-Eb5_hundred_twenty_eighth', 'note-Eb5_quarter',
                'note-Eb5_quarter.', 'note-Eb5_quarter..', 'note-Eb5_quarter._fermata', 'note-Eb5_quarter_fermata',
                'note-Eb5_sixteenth', 'note-Eb5_sixteenth.', 'note-Eb5_sixty_fourth', 'note-Eb5_thirty_second',
                'note-Eb5_whole', 'note-Eb5_whole.', 'note-Eb5_whole_fermata', 'note-Eb6_eighth', 'note-Eb6_eighth.',
                'note-Eb6_eighth..', 'note-Eb6_half', 'note-Eb6_half.', 'note-Eb6_quarter', 'note-Eb6_quarter.',
                'note-Eb6_quarter..', 'note-Eb6_sixteenth', 'note-Eb6_sixteenth.', 'note-Eb6_thirty_second',
                'note-F#2_eighth', 'note-F#2_eighth.', 'note-F#2_half', 'note-F#2_quarter', 'note-F#2_quarter.',
                'note-F#2_sixteenth', 'note-F#3_double_whole', 'note-F#3_eighth', 'note-F#3_eighth.', 'note-F#3_half',
                'note-F#3_half.', 'note-F#3_half_fermata', 'note-F#3_quarter', 'note-F#3_quarter.',
                'note-F#3_sixteenth', 'note-F#3_sixteenth.', 'note-F#3_thirty_second', 'note-F#3_whole',
                'note-F#3_whole.', 'note-F#4_double_whole', 'note-F#4_double_whole_fermata', 'note-F#4_eighth',
                'note-F#4_eighth.', 'note-F#4_eighth_fermata', 'note-F#4_half', 'note-F#4_half.',
                'note-F#4_half_fermata', 'note-F#4_quadruple_whole_fermata', 'note-F#4_quarter', 'note-F#4_quarter.',
                'note-F#4_quarter..', 'note-F#4_quarter._fermata', 'note-F#4_quarter_fermata', 'note-F#4_sixteenth',
                'note-F#4_sixteenth.', 'note-F#4_sixty_fourth', 'note-F#4_thirty_second', 'note-F#4_thirty_second.',
                'note-F#4_whole', 'note-F#4_whole.', 'note-F#4_whole._fermata', 'note-F#4_whole_fermata',
                'note-F#5_double_whole', 'note-F#5_eighth', 'note-F#5_eighth.', 'note-F#5_eighth_fermata',
                'note-F#5_half', 'note-F#5_half.', 'note-F#5_half._fermata', 'note-F#5_half_fermata',
                'note-F#5_quarter', 'note-F#5_quarter.', 'note-F#5_quarter..', 'note-F#5_quarter_fermata',
                'note-F#5_sixteenth', 'note-F#5_sixteenth.', 'note-F#5_sixty_fourth', 'note-F#5_thirty_second',
                'note-F#5_whole', 'note-F#5_whole.', 'note-F#5_whole_fermata', 'note-F#6_eighth', 'note-F#6_quarter',
                'note-F#6_quarter.', 'note-F#6_sixteenth', 'note-F#6_thirty_second', 'note-F#6_whole',
                'note-F2_double_whole', 'note-F2_double_whole.', 'note-F2_eighth', 'note-F2_eighth.', 'note-F2_half',
                'note-F2_half.', 'note-F2_quadruple_whole', 'note-F2_quarter', 'note-F2_quarter.', 'note-F2_sixteenth',
                'note-F2_whole', 'note-F2_whole.', 'note-F3_double_whole', 'note-F3_double_whole.',
                'note-F3_double_whole_fermata', 'note-F3_eighth', 'note-F3_eighth.', 'note-F3_half', 'note-F3_half.',
                'note-F3_half_fermata', 'note-F3_quadruple_whole', 'note-F3_quarter', 'note-F3_quarter.',
                'note-F3_quarter..', 'note-F3_sixteenth', 'note-F3_sixteenth.', 'note-F3_thirty_second',
                'note-F3_whole', 'note-F3_whole.', 'note-F3_whole_fermata', 'note-F4_double_whole',
                'note-F4_double_whole.', 'note-F4_double_whole_fermata', 'note-F4_eighth', 'note-F4_eighth.',
                'note-F4_eighth..', 'note-F4_eighth_fermata', 'note-F4_half', 'note-F4_half.', 'note-F4_half..',
                'note-F4_half._fermata', 'note-F4_half_fermata', 'note-F4_quadruple_whole', 'note-F4_quadruple_whole.',
                'note-F4_quadruple_whole_fermata', 'note-F4_quarter', 'note-F4_quarter.', 'note-F4_quarter..',
                'note-F4_quarter._fermata', 'note-F4_quarter_fermata', 'note-F4_sixteenth', 'note-F4_sixteenth.',
                'note-F4_sixty_fourth', 'note-F4_thirty_second', 'note-F4_whole', 'note-F4_whole.',
                'note-F4_whole_fermata', 'note-F5_double_whole', 'note-F5_eighth', 'note-F5_eighth.',
                'note-F5_eighth..', 'note-F5_half', 'note-F5_half.', 'note-F5_half._fermata', 'note-F5_half_fermata',
                'note-F5_quarter', 'note-F5_quarter.', 'note-F5_quarter..', 'note-F5_quarter._fermata',
                'note-F5_quarter_fermata', 'note-F5_sixteenth', 'note-F5_sixteenth.', 'note-F5_sixty_fourth',
                'note-F5_thirty_second', 'note-F5_whole', 'note-F5_whole.', 'note-F5_whole_fermata', 'note-F6_eighth',
                'note-F6_eighth.', 'note-F6_half', 'note-F6_half.', 'note-F6_quarter', 'note-F6_quarter.',
                'note-F6_sixteenth', 'note-F6_thirty_second', 'note-Fb3_eighth', 'note-Fb3_quarter', 'note-Fb4_eighth',
                'note-Fb4_quarter', 'note-Fb4_quarter.', 'note-Fb4_sixteenth.', 'note-Fb5_eighth', 'note-G#2_eighth',
                'note-G#2_eighth.', 'note-G#2_half', 'note-G#2_half.', 'note-G#2_quarter', 'note-G#2_quarter.',
                'note-G#2_sixteenth', 'note-G#3_eighth', 'note-G#3_eighth.', 'note-G#3_half', 'note-G#3_half.',
                'note-G#3_half_fermata', 'note-G#3_quarter', 'note-G#3_quarter.', 'note-G#3_sixteenth',
                'note-G#3_sixteenth.', 'note-G#3_thirty_second', 'note-G#3_whole', 'note-G#4_double_whole',
                'note-G#4_eighth', 'note-G#4_eighth.', 'note-G#4_eighth..', 'note-G#4_eighth._fermata', 'note-G#4_half',
                'note-G#4_half.', 'note-G#4_half._fermata', 'note-G#4_half_fermata', 'note-G#4_quarter',
                'note-G#4_quarter.', 'note-G#4_quarter_fermata', 'note-G#4_sixteenth', 'note-G#4_sixteenth.',
                'note-G#4_sixty_fourth', 'note-G#4_thirty_second', 'note-G#4_thirty_second.', 'note-G#4_whole',
                'note-G#4_whole.', 'note-G#4_whole_fermata', 'note-G#5_eighth', 'note-G#5_eighth.', 'note-G#5_half',
                'note-G#5_half.', 'note-G#5_half_fermata', 'note-G#5_quarter', 'note-G#5_quarter.',
                'note-G#5_quarter..', 'note-G#5_quarter_fermata', 'note-G#5_sixteenth', 'note-G#5_sixteenth.',
                'note-G#5_sixty_fourth', 'note-G#5_thirty_second', 'note-G#5_whole', 'note-G#5_whole.',
                'note-G2_double_whole', 'note-G2_double_whole.', 'note-G2_double_whole_fermata', 'note-G2_eighth',
                'note-G2_eighth.', 'note-G2_half', 'note-G2_half.', 'note-G2_half_fermata', 'note-G2_quadruple_whole',
                'note-G2_quarter', 'note-G2_quarter.', 'note-G2_quarter_fermata', 'note-G2_sixteenth',
                'note-G2_sixteenth.', 'note-G2_whole', 'note-G2_whole.', 'note-G3_double_whole',
                'note-G3_double_whole.', 'note-G3_eighth', 'note-G3_eighth.', 'note-G3_eighth._fermata',
                'note-G3_eighth_fermata', 'note-G3_half', 'note-G3_half.', 'note-G3_half_fermata',
                'note-G3_quadruple_whole', 'note-G3_quarter', 'note-G3_quarter.', 'note-G3_quarter..',
                'note-G3_quarter._fermata', 'note-G3_quarter_fermata', 'note-G3_sixteenth', 'note-G3_sixteenth.',
                'note-G3_thirty_second', 'note-G3_whole', 'note-G3_whole.', 'note-G3_whole_fermata',
                'note-G4_double_whole', 'note-G4_double_whole.', 'note-G4_double_whole_fermata', 'note-G4_eighth',
                'note-G4_eighth.', 'note-G4_eighth..', 'note-G4_eighth_fermata', 'note-G4_half', 'note-G4_half.',
                'note-G4_half._fermata', 'note-G4_half_fermata', 'note-G4_quadruple_whole', 'note-G4_quadruple_whole.',
                'note-G4_quadruple_whole_fermata', 'note-G4_quarter', 'note-G4_quarter.', 'note-G4_quarter..',
                'note-G4_quarter._fermata', 'note-G4_quarter_fermata', 'note-G4_sixteenth', 'note-G4_sixteenth.',
                'note-G4_sixteenth._fermata', 'note-G4_sixty_fourth', 'note-G4_thirty_second', 'note-G4_thirty_second.',
                'note-G4_whole', 'note-G4_whole.', 'note-G4_whole._fermata', 'note-G4_whole_fermata',
                'note-G5_double_whole', 'note-G5_double_whole.', 'note-G5_eighth', 'note-G5_eighth.',
                'note-G5_eighth..', 'note-G5_half', 'note-G5_half.', 'note-G5_half..', 'note-G5_half._fermata',
                'note-G5_half_fermata', 'note-G5_quarter', 'note-G5_quarter.', 'note-G5_quarter..',
                'note-G5_quarter._fermata', 'note-G5_quarter_fermata', 'note-G5_sixteenth', 'note-G5_sixteenth.',
                'note-G5_sixty_fourth', 'note-G5_thirty_second', 'note-G5_whole', 'note-G5_whole.',
                'note-G5_whole_fermata', 'note-Gb3_eighth', 'note-Gb3_half', 'note-Gb3_quarter', 'note-Gb3_quarter.',
                'note-Gb3_sixteenth', 'note-Gb4_eighth', 'note-Gb4_eighth.', 'note-Gb4_eighth..', 'note-Gb4_half',
                'note-Gb4_half.', 'note-Gb4_quarter', 'note-Gb4_quarter.', 'note-Gb4_sixteenth',
                'note-Gb4_sixty_fourth', 'note-Gb4_thirty_second', 'note-Gb4_whole', 'note-Gb5_eighth',
                'note-Gb5_eighth.', 'note-Gb5_half', 'note-Gb5_half.', 'note-Gb5_quarter', 'note-Gb5_quarter.',
                'note-Gb5_quarter..', 'note-Gb5_sixteenth', 'note-Gb5_sixteenth.', 'note-Gb5_thirty_second',
                'rest-eighth', 'rest-eighth.', 'rest-eighth..', 'rest-eighth._fermata', 'rest-eighth_fermata',
                'rest-half', 'rest-half.', 'rest-half._fermata', 'rest-half_fermata', 'rest-quadruple_whole',
                'rest-quarter', 'rest-quarter.', 'rest-quarter..', 'rest-quarter._fermata', 'rest-quarter_fermata',
                'rest-sixteenth', 'rest-sixteenth.', 'rest-sixteenth_fermata', 'rest-sixty_fourth',
                'rest-thirty_second', 'rest-whole', 'rest-whole.', 'rest-whole_fermata', 'tie', 'timeSignature-1/2',
                'timeSignature-1/4', 'timeSignature-12/16', 'timeSignature-12/4', 'timeSignature-12/8',
                'timeSignature-2/1', 'timeSignature-2/2', 'timeSignature-2/4', 'timeSignature-2/8',
                'timeSignature-24/16', 'timeSignature-3/1', 'timeSignature-3/2', 'timeSignature-3/4',
                'timeSignature-3/8', 'timeSignature-4/1', 'timeSignature-4/2', 'timeSignature-4/4', 'timeSignature-4/8',
                'timeSignature-5/4', 'timeSignature-6/16', 'timeSignature-6/2', 'timeSignature-6/4',
                'timeSignature-6/8', 'timeSignature-7/4', 'timeSignature-8/12', 'timeSignature-8/16',
                'timeSignature-8/2', 'timeSignature-8/4', 'timeSignature-9/16', 'timeSignature-9/8', 'timeSignature-C',
                'timeSignature-C/']


@tf.keras.utils.register_keras_serializable()
class CTCLayer(layers.Layer):

    def __init__(self, name=None, **kwargs):
        tf.keras.utils.custom_object_scope(
            *kwargs
        )
        super(CTCLayer, self).__init__(**kwargs)
        self.loss_fn = keras.backend.ctc_batch_cost

    def call(self, y_true, y_pred):
        # Compute the training-time loss value and add it
        # to the layer using `self.add_loss()`.
        batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
        input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
        label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")

        input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
        label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")

        loss = self.loss_fn(y_true, y_pred, input_length, label_length)
        self.add_loss(loss)

        # At test time, just return the computed predictions
        return y_pred

    def get_config(self):
        config = super(CTCLayer, self).get_config()
        return config


def get_model():
    global model, prediction_model
    model = load_model("C:/Users/shalev/PycharmProjects/pictureServer/my_model.h5",
                       custom_objects={"CTCLayer": CTCLayer})
    prediction_model = keras.models.Model(
        model.get_layer(name="image").input, model.get_layer(name="dense2").output
    )
    print("model loaded")


print("loading model")
get_model()


def remove_alpha_channel(image):
    if image.mode in ["RGBA", "P"]:
        image = image.convert("RGB")
    return image


def trim_borders(image):
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)

    return image


def pad_image(image):
    return ImageOps.expand(image, border=30, fill='#fff')


def resize_image(image):
    # return tf.image.resize(image, [img_height, img_width])
    return image.resize((2000, 200), Image.LINEAR)


def to_grayscale(image):
    return image.convert('L')


def invert_colors(image):
    return ImageOps.invert(image)


def expand_dims(image):
    image = np.expand_dims(image, -1)
    image = image[None]
    print(image.shape)

    return image


@app.route('/', methods=['GET'])
def sendModelToClient():
    response = jsonify({'result': 'data'})
    # response.headers.add('Access-Control-Allow-Origin', '*')
    return response


char_to_num = layers.StringLookup(
    vocabulary=list(uniqueLabels), mask_token=None)
num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)
img_width = 2000
img_height = 200


def encode_single_sample(img_path):
    # 1. Read image
    # img = tf.io.read_file(img_path)
    # 2. Decode and convert to grayscale
    # img = tf.io.decode_png(img, channels=1)
    # 3. Convert to float32 in [0, 1] range
    img = tf.image.convert_image_dtype(img_path, tf.float32)
    # 4. Resize to the desired size
    img = tf.image.resize(img, [img_height, img_width])
    # img = img.resize((200, 2000), Image.LINEAR)
    #     # 5. Transpose the image because we want the time
    #     # dimension to correspond to the width of the image.
    img = tf.transpose(img, perm=[1, 0, 2])
    # 6. Map the characters in label to numbers
    return {"image": img}

def decode_from_prediction(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
              :, :max_length
              ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = num_to_char(res)
        output_text.append(res)
    return output_text


    batch_images = tf.io.read_file('./demo.png')
    preds = prediction_model.predict(batch_images)
    pred_texts = decode_batch_predictions(preds)

def decode_batch_predictions(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
              :, :max_length
              ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = num_to_char(res)
        output_text.append(res)
    return output_text

    #  Let's check results on some validation samples
    # for batch in validation_dataset.take(1):
    #     batch_images = 'demo.png'
    #     batch_labels = batch["label"]
    batch_images = tf.io.read_file('./demo.png')
    preds = prediction_model.predict(batch_images)
    pred_texts = decode_batch_predictions(preds)

    orig_texts = []
    for label in batch_labels:
        label = num_to_char(label)
        orig_texts.append(label)

    img = (batch_images[i, :, :, 0] * 255).numpy().astype(np.uint8)
    img = img.T
    title = f"Prediction: {pred_texts[i]}"
    plt.imshow(img, cmap="gray")
    plt.axis("off")
    plt.plot()

    plt.show()

    print("label: ", orig_texts)
    print("prediction: ", pred_texts)


@app.route('/predict', methods=['POST'])
def predict():
    print(prediction_model)
    prediction_model.summary()

    image_data = request
    print(image_data.data.__str__())

    preprocessImage = image_data.data.__str__()
    strImage = preprocessImage.split("base64,")[1]
    bytes_encoded = bytes(strImage, encoding="ascii")

    bytesImgIO = io.BytesIO(bytes_encoded)
    bytesImgIO.seek(0)
    bytesImg = bytesImgIO.read()

    im = Image.open(BytesIO(base64.b64decode(bytes_encoded)))
    im = remove_alpha_channel(im)
    im = to_grayscale(im)
    im = trim_borders(im)
    im = pad_image(im)
    im = resize_image(im)

    # im = tf.io.decode_png(im, channels=1)
    im = tf.image.convert_image_dtype(im, tf.float32)

    test_im = im
    test_im = tf.transpose(test_im)
    if test_im.shape == (2000, 200):
        im = expand_dims(im)

    im = tf.transpose(im)

    preds = prediction_model.predict(im)
    predication = decode_batch_predictions(preds)
    print(predication)
    result = predication

    resStr = result[0].__str__();
    response = jsonify({'result': resStr})

    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
