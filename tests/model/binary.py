

class BinaryModel(object):

    file = File(config.fileName)
    
    def __init__(self, directory):
        self.directory = directory

    def create(self, doc):
        return file.perform(write(json.dumps(doc)), doc=doc)
    
    def read(self, doc_id):
        buf = file.perform(read(), doc_id)
        doc = json.loads(buf)   # TODO: may have problems with documents larger than max_buf
        return doc
    
    def update(self, doc):
        return file.perform(write(json.dumps(doc)), doc=doc)
    
    def delete(self, doc_id):
        filepath = file._get_file_handle(doc_id)
        os.unlink(filepath)
        return True
