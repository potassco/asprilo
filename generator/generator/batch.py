import yaml
import pprint

class BatchProc(object):
    """Batch Processor for Instance Generation.

    """

    def __init__(self, fpath):
        """Init.
        
        """        
        self.fpath = fpath
        self.file = open(fpath, 'r')
        self.content = yaml.load(self.file.read())


    def run(self):
        """Run jobs.
        
        """
        pass

# bp = BatchProc("../scripts/batch/test.yml")
# pprint.pprint(bp.content)
