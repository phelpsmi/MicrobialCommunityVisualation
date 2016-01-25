
class sample:
    organism_count = 0
    sample_count = 0
    microbe_ids = []
    data_by_sample = [][]
    data_by_microbe = [][]

    #Class: initializer
    #input: file_name -> string location to file
    #May end up having the file loaded in seperately
    def __init__(self, file_name):
        parsed_file = open_file(file_name)
        sample_count = len(parsed_file[0]-1)
        organism_count = len(parsed_file)
        for microbe in parsed_file:
            microbe_ids[] = microbe[0]
            data_by_microbe[] = map(float, microbe)
            for idx, sample in microbe[1:]:
                data_by_sample[idx][] = float(sample)

    def open_file(file_name):
        if file_name.endswith('.otu'):
            return list(csv.reader(open(file_name, 'rb'), delimiter='\t'))
        return 0

    def get_sample(self, index):
        return data_by_sample[inex]

    def get_microbes(self, index):
        if type(index) is str:
            for i, microbe_id in microbe_ids:
                if index == microbe_id:
                    return data_by_microbe[i]
        elif type(index) is int:
            return data_by_microbe[index]
