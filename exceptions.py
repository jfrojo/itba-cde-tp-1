class ProductNotInsertedException(Exception):

    def __init__(self, name, product_type):
        self.name = name
        self.type = product_type
        super().__init__('the product (name: \'{}\', type: \'{}\') could not be inserted'.format(name, product_type))

class IssueNotInsertedException(Exception):

    def __init__(self, name, issue_type):
        self.name = name
        self.type = issue_type
        super().__init__('the issue (name: \'{}\', type: \'{}\') could not be inserted'.format(name, issue_type))

class StateNotInsertedException(Exception):

    def __init__(self, name):
        self.name = name
        super().__init__('the state (name: \'{}\') could not be inserted'.format(name))

class CompanyNotInsertedException(Exception):

    def __init__(self, name):
        self.name = name
        super().__init__('the company (name:\'{}\') could not be inserted'.format(name))

class ComplaintNotInsertedException(Exception):

    def __init__(self, id):
        self.id = id
        super().__init__('the complaint (id: \'{}\') could not be inserted'.format(id))

class TagNotInsertedException(Exception):

    def __init__(self, tag):
        self.id = tag
        super().__init__('the tag (name: \'{}\') could not be inserted'.format(tag))

class ComplaintTagNotInsertedException(Exception):

    def __init__(self, complaint_id, tag_id):
        self.complaint_id = complaint_id
        self.tag_id = tag_id
        super().__init__('the tag (complaint_id: \'{}\', tag_id: \'{}\')'.format(complaint_id, tag_id))
