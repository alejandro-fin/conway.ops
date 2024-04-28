

class DataHubSchema():

    '''
    This class contains statics used to define the structure of DataHubs used by the {{ p.app }} application.
    '''
    def __init__(self):
        pass


    MARKET_DATA_REGIONS                         = "regions"
    '''
    Name of a dataset containing prices for all regions. It is stored as an Excel file with one worksheet per region.
    '''

    PRODUCT_COL                                 = "Product"
    '''
    Name of a column used by datasets that contain product information (such as a product's unit cost)
    '''

    UNIT_COST_COL                               = "Unit Cost"
    '''
    Name of a column used by datasets that record the unit cost per product,  for a list of products.
    '''

    AMOUNT_COL                                  = "Amount"
    '''
    Name of a column used by datasets that record the number of units per product, for a list of products
    '''