"""
Credit to the parker library (https://github.com/coxmediagroup/parker/) and their TastyPieHandler.
"""

req = HttpRequest()
resource = YourResource()

bundle = resource.build_bundle(obj=your_model)
bundle = resource.full_dehydrate(bundle)
bundle = resource.alter_detail_data_to_serialize(req, bundle)

json_string = resource.serialize(req, bundle, 'application/json')