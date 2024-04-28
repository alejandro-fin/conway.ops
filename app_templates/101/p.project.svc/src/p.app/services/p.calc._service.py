import pandas                                                       as _pd

from conway.application.application                                 import Application as {{ APP() }}
from conway.database.data_accessor                                  import DataAccessor

from conway.util.dataframe_utils                                    import DataFrameUtils
from conway.util.profiler                                           import Profiler

from {{ p.app }}.util.static_globals                      import DataHubSchema

class {{ pascal(p.calc) }}Service():

    '''
    Sample service to illustrate how to write services that perform calculations

    :param {{ pascal(p.calc) }}ServiceConfig config: object containing all settings needed by an instance of the
        {{ pascal(p.calc) }}Service
    '''
    def __init__(self, config):
        self.config                                     = config

    def get_{{ pascal(p.calc_resource) }}(self, bid):
        '''
        Computes a price for a bid involving a number of products and services, and generates and returns a DataFrame that contains 
        the details of what the products and services it covers, as well as the itemized pricing for each item.

        :param dict bid: A dictionary of properties for the bid to be priced, including a subdictionary defining the scope of the 
            bid. For that sub-dictinoary, keys represent the various products and services in the scope of the quote,
            and the dictionary values represent the number of units for each product or service.

        :returns: A DataFrame with 3 columns, for the product, the amount, and the total cost.
        :rtype: ``pandas.DataFrame``
        '''
        with Profiler("Calculating a {{ pascal(p.calc_resource) }}"):
            DHS                                             = DataHubSchema()
            customer                                        = bid["customer_name"]
            region                                          = bid["region"]
            scope_dict                                      = bid["scope"] # This determines which products/amounts are included in the order

 

            {{ APP() }}.app().log(f"Loading input data for region {region}")
            # Input data for regions is stored in an Excel spreadsheet, with a dedicated tab per region. The Excel tab
            # determines the ``subpath`` parameter in the DataAccessor context manager
            #
            {{ p.in_hub }}_path                                = f"{self.config.{{ p.in_hub }}_hub}/{DHS.MARKET_DATA_REGIONS}"
            with DataAccessor({{ p.in_hub }}_path, subpath=region) as ax:
                regional_input_df                           = ax.retrieve()

            {{ APP() }}.app().log(f"Pricing quote for {customer}")
            scope_df                                        = _pd.DataFrame({DHS.PRODUCT_COL: list(scope_dict.keys()),
                                                                            DHS.AMOUNT_COL: list(scope_dict.values())})                                

            # regional_input_df is expected to contain two columns: one to identify the product, one for unit costs.
            # We want to join those unit costs for the products/amounts that are in scope_df
            #
            joinable_df                                     = regional_input_df.set_index(DHS.PRODUCT_COL)

            result_df                                       = scope_df.join(joinable_df, on=DHS.PRODUCT_COL)

            result_df["Total"]                              = result_df[DHS.AMOUNT_COL] * result_df[DHS.UNIT_COST_COL]

            return result_df