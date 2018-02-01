import bokeh.embed
import bokeh.io
import bokeh.models
import bokeh.models.widgets
import bokeh.plotting
import pandas as pd
from pandas_datareader import wb

bokeh.plotting.output_notebook()

df = wb.download(indicator='NY.GDP.PCAP.KD', country=['US', 'CA', 'MX'], start=2005, end=2008)
df = df.reset_index()

source = bokeh.models.ColumnDataSource(df)
original_source = bokeh.models.ColumnDataSource(df)
columns = [
    bokeh.models.widgets.TableColumn(field="country", title="Country"),
    bokeh.models.widgets.TableColumn(field="year", title="Year"),
    bokeh.models.widgets.TableColumn(field="NY.GDP.PCAP.KD", title="NY.GDP.PCAP.KD"),
]
data_table = bokeh.models.widgets.DataTable(source=source, columns=columns)

# callback code to be used by all the filter widgets
# requires (source, original_source, country_select_obj, year_select_obj, target_object)
combined_callback_code = """
var data = source.get('data');
var original_data = original_source.get('data');
var country = country_select_obj.get('value');
console.log("country: " + country);
var year = year_select_obj.get('value');
console.log("year: " + year);

for (var key in original_data) {
    data[key] = [];
    for (var i = 0; i < original_data['country'].length; ++i) {
        if ((country === "ALL" || original_data['country'][i] === country) &&
            (year === "ALL" || original_data['year'][i] === year)) {
            data[key].push(original_data[key][i]);
        }
    }
}
target_obj.trigger('change');
source.trigger('change');
"""

# define the filter widgets, without callbacks for now
country_list = ['ALL'] + df['country'].unique().tolist()
country_select = bokeh.models.widgets.Select(title="Country:", value=country_list[0], options=country_list)
year_list = ['ALL'] + df['year'].unique().tolist()
year_select = bokeh.models.widgets.Select(title="Year:", value=year_list[0], options=year_list)

# now define the callback objects now that the filter widgets exist
generic_callback = bokeh.models.CustomJS(
    args=dict(source=source, 
              original_source=original_source, 
              country_select_obj=country_select, 
              year_select_obj=year_select, 
              target_obj=data_table),
    code=combined_callback_code
)

# finally, connect the callbacks to the filter widgets
country_select.callback = generic_callback
year_select.callback = generic_callback

p = bokeh.io.vplot(country_select, year_select, data_table)
bokeh.plotting.show(p)