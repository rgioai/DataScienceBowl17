import numpy as np
import h5py
import os

"""
=================================================================================
For this branch (modular_preprocess), I have yet to implement full h5py
functionality.  Eventually, it looks like we will need a chunk-oriented save
operation.  This is not an issue initally with sample images, but will cause
problems in the larger datasets.
=================================================================================
"""


def make_dataset(top_directory, x=512, y=512, slices=100, mode=None,
                 processing='', mirroring_axes=None, chunk_size=10):
    """
    Applys function parameters to make an h5py dataset of all patients in top_directory.
    :param top_directory: path to directory with patient directories
    :param x: x dimension of output
    :param y: y dimension of output
    :param slices: number of slices in output
    :param mode: None or one of 'constant', 'edge', 'symmetric', 'reflect', 'wrap'
    :param processing: 'hu'
    :param mirroring_axes: None or one or more of ['lr', 'ud', 'fb']
    :param chunk_size: Number of patients per h5f chunk.
    """
    chunk_array = None
    i = 0
    total = len(os.listdir(top_directory))
    #h5f = h5py.File('/nvme/candidate_datasets/%s' % name_dataset(x=x, y=y, slices=slices, mode=mode,
    #                             processing=processing, mirroring_axes=mirroring_axes), 'w')

    for patient_dir in os.listdir(top_directory):
        if slices < 0:
            from two_d import two_d_preprocess
            processed_patient = two_d_preprocess('%s/%s' % (top_directory, patient_dir), x=x, y=y, mode=mode,
                                                 processing=processing, mirroring_axes=mirroring_axes)
        else:
            from three_d import three_d_preprocess
            processed_patient = three_d_preprocess('%s/%s' % (top_directory, patient_dir), x=x, y=y, slices=slices,
                                                   mode=mode, processing=processing, mirroring_axes=mirroring_axes)
        i += 1
        if i % chunk_size == 0 and not chunk_size == -1:
            # SPRINT2 Save dataset_array to h5f and reset chunk_array
            chunk_array = None
            # SPRINT2 Handle data splits in an efficient way (train/test; x/y)
        else:
            #print(chunk_array.shape)
            #print(processed_patient.shape)
            if chunk_array is None:
                chunk_array = processed_patient
            else:
                chunk_array = array_merge(chunk_array, processed_patient)

        # Report progress
        print('\rProgress: %.2f' % float((i/total) * 100), end='')

    if chunk_size == -1:
        import pickle
        name = name_dataset(x=x, y=y, slices=slices, mode=mode, processing=processing, mirroring_axes=mirroring_axes)
        name = name[:-2] + 'np'
        with open(name, 'wb') as f:
            pickle.dump(chunk_array, f)
            f.close()


def array_merge(dataset_array, new_example_array):
    return np.vstack((dataset_array, new_example_array))


def name_dataset(x, y, slices, mode, processing, mirroring_axes):
    if mode is None:
        mode = 'constant'  # default
    if processing == '':
        processing = 'hu'  # default
    if mirroring_axes is None:
        mirroring_axes = 'none'  # default
    if slices <= 0:
        return '2D_%dx%d_%s_%s_%s.h5' % (x, y, mode, processing, mirroring_axes)
    else:
        return '3D_%dx%dx%d_%s_%s_%s.h5' % (x, y, slices, mode, processing, mirroring_axes)


if __name__ == '__main__':
    import unittest
    import pickle


    class TestMakeDataset(unittest.TestCase):
        def setUp(self):
            self.params_2d = {'x': 100, 'y': 100, 'slices': -1, 'mode': None, 'processing': '', 'mirroring_axes': None}
            self.name_2d = '2D_100x100_constant_hu_none.np'
            self.params_3d = {'x': 100, 'y': 100, 'slices': 50, 'mode': None, 'processing': '', 'mirroring_axes': None}
            self.name_3d = '3D_100x100x50_constant_hu_none.np'

        def test_array_merge(self):
            a = np.array([[[[101, 102, 103], [104, 105, 106], [107, 108, 109]],
                           [[111, 112, 113], [114, 115, 116], [117, 118, 119]],
                           [[121, 122, 123], [124, 125, 126], [127, 128, 129]]], 0])

            b = np.array([[[[211, 212, 213], [214, 215, 216], [217, 218, 219]],
                           [[221, 222, 223], [224, 225, 226], [227, 228, 229]],
                           [[231, 232, 233], [234, 235, 236], [237, 238, 239]]], 1])

            c = np.array([[[[301, 302, 303], [304, 305, 306], [307, 308, 309]],
                           [[311, 312, 313], [314, 315, 316], [317, 318, 319]],
                           [[321, 322, 323], [324, 325, 326], [327, 328, 329]]], 0])

            sub1 = array_merge(a, b)
            sub2 = array_merge(sub1, c)

            self.assertEqual(sub1.shape, (2, 2))
            self.assertEqual(sub2.shape, (3, 2))
            # self.assertEqual(sub1[0], a)
            self.assertEqual(sub1[0][1], 0)
            # self.assertEqual(sub2[2], c)
            self.assertEqual(sub2[2][1], 0)
            # FUTURE Fix all tests
            # Two tests removed because type conversions within numpy modify elements and prevent proper comparison
            # Either improve test cases (np arrays of np arrays instead of np arrays of lists) or modify tests

        def test_name_dataset(self):
            self.assertEqual(name_dataset(self.params_2d['x'], self.params_2d['y'], self.params_2d['slices'],
                                          self.params_2d['mode'], self.params_2d['processing'],
                                          self.params_2d['mirroring_axes']),
                             '2D_100x100_constant_hu_none.h5')
            self.assertEqual(name_dataset(self.params_3d['x'], self.params_3d['y'], self.params_3d['slices'],
                                          self.params_3d['mode'], self.params_3d['processing'],
                                          self.params_3d['mirroring_axes']),
                             '3D_100x100x50_constant_hu_none.h5')

        def test_make_3d_dataset(self):
            make_dataset('/nvme/stage1_data/sample_images', x=self.params_3d['x'], y=self.params_3d['y'],
                         slices=self.params_3d['slices'], mode=self.params_3d['mode'],
                         processing=self.params_3d['processing'], mirroring_axes=self.params_3d['mirroring_axes'],
                         chunk_size=-1)
            with open(self.name_3d, 'rb') as f:
                ds = pickle.load(f)
                f.close()

            self.assertEqual(ds.shape, (len(os.listdir('/nvme/stage1_data/sample_images')), 2))

            self.assertEqual(ds[0].shape, (2,))
            self.assertEqual(ds[0][0].shape, (self.params_3d['slices'],
                                              self.params_3d['x'],
                                              self.params_3d['y']))
            self.assertIsInstance(ds[0][1], int)

            self.assertEqual(ds[1].shape, (2,))
            self.assertEqual(ds[1][0].shape, (self.params_3d['slices'],
                                              self.params_3d['x'],
                                              self.params_3d['y']))
            self.assertIsInstance(ds[1][1], int)

            os.remove(self.name_3d)

        def test_make_2d_dataset(self):
            make_dataset('/nvme/stage1_data/sample_images', x=self.params_2d['x'], y=self.params_2d['y'],
                         slices=self.params_2d['slices'], mode=self.params_2d['mode'],
                         processing=self.params_2d['processing'], mirroring_axes=self.params_2d['mirroring_axes'],
                         chunk_size=-1)
            with open(self.name_2d, 'rb') as f:
                ds = pickle.load(f)
                f.close()

            self.assertEqual(ds.shape, (len(os.listdir('/nvme/stage1_data/sample_images')), 2))

            self.assertEqual(ds[0].shape, (2,))
            self.assertEqual(ds[0][0].shape[1], self.params_2d['x'])
            self.assertEqual(ds[0][0].shape[2], self.params_2d['y'])

            self.assertIsInstance(ds[0][1], int)

            self.assertEqual(ds[1].shape, (2,))
            self.assertEqual(ds[1][0].shape[1], self.params_2d['x'])
            self.assertEqual(ds[1][0].shape[2], self.params_2d['y'])
            self.assertIsInstance(ds[1][1], int)

            os.remove(self.name_2d)

        def tearDown(self):
            pass

    unittest.main(verbosity=2)