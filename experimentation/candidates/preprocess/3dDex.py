"""
3dDex - SentDex: 3D Adaptation
"""


def 3dDex(abspath, dim_px=50, dim_slice=20):

    data_dir = abspath
    patients = os.listdir(abspath)
    labels_df = pd.read_csv(data_dir + 'stage1_labels.csv', index_col=0)

    def chunks(l, n):
        # Credit: Ned Batchelder
        # Link: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def mean(a):
        return sum(a) / len(a)

    def process_data(patient, labels_df, img_px_size=50, hm_slices=20):
        label = labels_df.get_value(patient, 'cancer')
        path = data_dir + patient
        slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
        slices.sort(key = lambda x: int(x.ImagePositionPatient[2]))

        new_slices = []
        slices = [cv2.resize(np.array(each_slice.pixel_array),(dim_px,dim_px)) for each_slice in slices]
        
        chunk_sizes = math.ceil(len(slices) / hm_slices)
        for slice_chunk in chunks(slices, chunk_sizes):
            slice_chunk = list(map(mean, zip(*slice_chunk)))
            new_slices.append(slice_chunk)

        while len(new_slices) != hm_slices:
            if len(new_slices) < hm_slices:
                new_slices.append(new_slices[-1])
            else:
                new_val = list(map(mean, zip(*[new_slices[hm_slices-1],new_slices[hm_slices],])))
                del new_slices[hm_slices]
                new_slices[hm_slices-1] = new_val
            
        if label == 1:
            label=np.array([0,1])
        elif label == 0:
            label=np.array([1,0])
            
        return np.array(new_slices),label


    3d_proc = []

    for num,patient in enumerate(patients):
        try:
            img_data,label = process_data(patient,labels_df,dim_px,dim_slice)
            3d_proc.append([img_data,label])
        except KeyError as e:
            pass

    #np.save('3dProc-{}-{}-{}.npy'.format(dim_px,dim_px,dim_slice), 3d_proc)
    return 3d_proc
