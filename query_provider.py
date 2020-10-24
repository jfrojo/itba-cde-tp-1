import utils

def get_tag_query(tag):
    if(tag is None):
        return {'query': 'SELECT * FROM tags WHERE name IS NULL', 'params': []}

    return {'query': 'SELECT * FROM tags WHERE name = %s', 'params': [tag]}

def get_product_query(product_name, product_type):
    if(utils.is_none(product_name)):
        if(utils.is_none(product_type)):
            return {'query': 'SELECT * FROM products WHERE name IS NULL AND type IS NULL', 'params': []}
        else :
            return {'query': 'SELECT * FROM products WHERE name IS NONE AND type = %s', 'params': [product_type]}
    else:
        if(utils.is_none(product_type)):
            return {'query': 'SELECT * FROM products WHERE name = %s AND type IS NULL', 'params': [product_name]}
        else:
            return {'query': 'SELECT * FROM products WHERE name = %s AND type = %s', 'params': [product_name, product_type]}

def get_issue_query(issue_name, issue_type):
    if(utils.is_none(issue_name)):
        if(utils.is_none(issue_type)):
            return {'query': 'SELECT * FROM issues WHERE name IS NULL AND type IS NULL', 'params': []}
        else:
            return {'query': 'SELECT * FROM issues WHERE name IS NULL AND type = %s', 'params': [issue_type]}
    else:
        if(utils.is_none(issue_type)):
            return {'query': 'SELECT * FROM issues WHERE name = %s AND type IS NULL', 'params': [issue_name]}
        else:
            return {'query': 'SELECT * FROM issues WHERE name = %s AND type = %s', 'params': [issue_name, issue_type]}

def get_company_query(company_name):
    if(utils.is_none(company_name)):
        return {'query': 'SELECT * FROM companies WHERE name IS NULL', 'params': []}
    else:
        return {'query': 'SELECT * FROM companies WHERE name = %s', 'params': [company_name]}

def get_state_query(state_name):
    if(utils.is_none(state_name)):
        return {'query': 'SELECT * FROM states WHERE name IS NULL', 'params': []}
    
    return {'query': 'SELECT * FROM states WHERE name = %s', 'params': [state_name]}
